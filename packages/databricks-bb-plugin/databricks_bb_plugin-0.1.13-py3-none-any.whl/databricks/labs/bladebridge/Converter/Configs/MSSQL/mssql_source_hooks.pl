use strict;
use Data::Dumper;

my $MR = new Common::MiscRoutines(MESSAGE_PREFIX => 'MSSQL_HOOKS');
my %CFG = (); #entries to be initialized
my $CFG_POINTER = undef;
my $CONVERTER = undef;
my $INDENT = 0; #keep track of indents
my %PRESCAN = ();
my %USE_VARIABLE_QUOTE = ();
my $RETURN_TYPE = '';
my $EXCEPTIONS = {};
my $LAST_EXCEPTION_NAME = '';
my $CATALOG;
my $VARIABLE_PREFIX = 'v_';


my $STANDARD_CATCH_BLOCK = '
	result = "Failed: %CONVERT_TYPE%: " + %STANDARD_VAR%_name + "\n Step: " + %STANDARD_VAR%_step + "\n Code: " + err.code + "\n  State: " + err.state;
	result += "\n  Message: " + err.message;
	result += "\nStack Trace:\n" + err.stackTraceTxt;
	err.message_detail=result;
	return err;';

my @VARIABLE_TYPE_PATTERNS_WITH_QUOTES = ( #these are the patterns of data types that require including single quotes when applying ` + var + ` in function JS_substitute
	"char",
	"date",
	"time",
	"text"
);

sub init_mssql_hooks #register this function in the config file
{
	my $param = shift;
	%CFG = %{$param->{CONFIG}};
	$CFG_POINTER = $param->{CONFIG}; #give the ability to modify config incrementally
	$Globals::ENV{CFG_POINTER} = \%CFG;
	$CONVERTER = $param->{CONVERTER} unless $CONVERTER;
	$MR = new Common::MiscRoutines unless $MR;
	print "INIT_HOOKS Called. MR: $MR. config:\n" . Dumper(\%CFG);


	#Reinitilize vars for when -d option is used:
	$INDENT = 0; #keep track of indents
	%PRESCAN = ();
	%USE_VARIABLE_QUOTE = ();
	$RETURN_TYPE = '';
	$EXCEPTIONS = {};
	$LAST_EXCEPTION_NAME = '';
}

sub var_need_quote
{
	my $type = shift;
	foreach my $t (@VARIABLE_TYPE_PATTERNS_WITH_QUOTES)
	{
		return 1 if ($type =~ /$t/gis)
	}
	return 0;
}

#uses PRESCAN structure to catalog dat types
sub catalog_var_datatypes
{
	if ($PRESCAN{ARG_TYPE})
	{
		foreach my $pos (keys %{$PRESCAN{ARG_TYPE}})
		{
			my $type = $PRESCAN{ARG_TYPE}->{$pos};
			my $arg_name = $PRESCAN{ARG_NAME}->{$pos};
			next unless $arg_name;
			$USE_VARIABLE_QUOTE{$arg_name} = var_need_quote($type);
			$USE_VARIABLE_QUOTE{uc($arg_name)} = var_need_quote($type);
		}
	}

	if ($PRESCAN{PROC_VARS})
	{
		foreach my $v (keys %{$PRESCAN{PROC_VARS}})
		{
			my $x = $PRESCAN{PROC_VARS}->{$v};
			next unless $x->{VARNAME};
			$USE_VARIABLE_QUOTE{$x->{VARNAME}} = var_need_quote($x->{VARTYPE});
			$USE_VARIABLE_QUOTE{uc($x->{VARNAME})} = var_need_quote($x->{VARTYPE});
		}
	}
}

sub code_indent
{
	my $code = shift;
	return $code unless $CFG{code_indent};
	my @lines = split(/\n/, $code);
	foreach my $ln (@lines)
	{
		my $spaces = '';
		my $cfg_indents = $CFG{code_indent} =~ tr/\t//;
		$cfg_indents--;
		for(my $i=0; $i<$INDENT + $cfg_indents; $i++)
		{
			$spaces .= "\t";
		}
		$ln = $spaces . $ln;
	}
	my $ret = join("\n", @lines);

	$ret =~ s/\;\s*$//gis; #get rid of trailing semicolon
	$ret =~ s/\s*$//gis;
	$MR->log_msg("code_indent:: ''''$ret''''");
	return $ret;
}

# should be called by prescan_and_collect_info_hook in sql converter
sub mssql_prescan
{
	my $cont = shift;
	$Globals::ENV{PRESCAN} = ();
	print "******** prescan_code_mssql $cont *********\n";
	my $ret = {}; #hash to keep everything that needs to be captured

	$cont =~ s/@/$VARIABLE_PREFIX/ig;
	my $proc_args = '';
	my $proc_vars = '';
	my $proc_name = '';
	
	$cont =~ s/\bALTER\s+PROCEDURE\b/CREATE PROCEDURE/gis;
	
	if ($cont =~ /CREATE\s+PROC\s+(\w+\.\w+)(.*?)AS\b/gis)
	{
		$proc_name = $MR->trim($1);
		$proc_args = $MR->trim($2);
	}
	elsif($cont =~ /CREATE\s+PROC\s+(\[\w+\]\.\[\w+\])(.*?)AS\b/gis)
	{
		$proc_name = $MR->trim($1);
		$proc_args = $MR->trim($2);
	}
	elsif ($cont =~ /CREATE\s+PROCEDURE\s+(\w+\.\w+)(.*?)AS\b/gis)
	{
		$proc_name = $MR->trim($1);
		$proc_args = $MR->trim($2);
	}
	elsif($cont =~ /CREATE\s+PROCEDURE\s+(\[\w+\]\.\[\w+\])(.*?)AS\b/gis)
	{
		$proc_name = $MR->trim($1);
		$proc_args = $MR->trim($2);
	}	
	else
	{
		$MR->log_msg("Cannot find proc args");
	}
	$proc_name =~s/\]//g;
	$proc_name =~s/\[//g;
	
	$proc_args =~s/\]//g;
	$proc_args =~s/\[//g;

					 
	$Globals::ENV{PRESCAN}->{PROC_NAME} = $proc_name;
	
	my @proc_args = map { $MR->trim($_) } split(/,/, $proc_args);
	my $pos = 0;
	foreach my $pa (@proc_args)
	{
		$pos++;
		$Globals::ENV{PRESCAN}->{ARG}->{$pos} = $pa;
		my @tmp = split(/ /, $pa);
		my $arg_name = shift(@tmp);
		my $arg_type = shift(@tmp);
		$Globals::ENV{PRESCAN}->{ARG_NAME}->{$pos} = uc($arg_name);
		$Globals::ENV{PRESCAN}->{ARG_TYPE}->{$pos} = $arg_type;
		my $arg_dir = shift(@tmp);
		if($arg_dir eq "OUTPUT" or $arg_dir eq "OUT")
		{
			$RETURN_TYPE = $arg_type;
		}
	}

	if(uc($cont) =~ /AS([\s\S]+)/)
	{
		my $body = $1;
		
		my @vars = ();
		my @caught_declares = ();
		if($body =~ /DECLARE\s+(.*?)\bBEGIN\b\s+\bTRY\b/gis)
		{
			@caught_declares = "$body" =~ /DECLARE\s+.*?\bBEGIN\b\s+\bTRY\b/gis;
		}
		elsif($body =~ /DECLARE\s+.*?\b(SET|SELECT|INSERT|UPDATE)\b/gis)
		{
			@caught_declares = "$body" =~ /DECLARE\s+(.*?)\b(?:SET|SELECT|INSERT|UPDATE)\b/gis;
		}
		if ($#caught_declares > -1)
		{
            my $var_pos = 0;
			$MR->log_msg("DECLARE FOUND VARIANT 1: $1");

			foreach my $item (@caught_declares)
			{
				my @vars = get_proc_var($1);
				foreach my $item (@vars)
				{
					$var_pos++;
					my ($varname, $vartype, $default) = ('','','');
					if($item =~ /(\w+)\s+([\w|\(|\)]+)\s*\=\s*(.*)\s*/g)
					{
						$varname = $1;
						$vartype = $2;
						$default = $3;
						$Globals::ENV{PRESCAN}->{PROC_VARS}->{$var_pos} = {VARNAME => $varname, VARTYPE => $vartype, DEFAULT => $default};
					}
					elsif($item =~ /(\w+)\s+([\w|\(|\)]+)/g)
					{
						$varname = $1;
						$vartype = $2;
						$Globals::ENV{PRESCAN}->{PROC_VARS}->{$var_pos} = {VARNAME => $varname, VARTYPE => $vartype, DEFAULT => $default};
					}
				}				
			}
        }
        
		#if($body =~ /DECLARE\s+(.*?)\bBEGIN\b\s+\bTRY\b/gis or $body =~ /DECLARE\s+(.*?)\b(SET|SELECT|INSERT|UPDATE)\b/gis)
		#{
		#	my $var_pos = 0;
		#	$MR->log_msg("DECLARE FOUND VARIANT 1: $1");
		#
		#	my @vars = get_proc_var($1);
		#	foreach my $item (@vars)
		#	{
		#		$var_pos++;
		#		my ($varname, $vartype, $default) = ('','','');
		#		if($item =~ /(\w+)\s+([\w|\(|\)]+)\s*\=\s*(.*)\s*/g)
		#		{
		#			$varname = $1;
		#			$vartype = $2;
		#			$default = $3;
		#			$Globals::ENV{PRESCAN}->{PROC_VARS}->{$var_pos} = {VARNAME => $varname, VARTYPE => $vartype, DEFAULT => $default};
		#		}
		#		elsif($item =~ /(\w+)\s+([\w|\(|\)]+)/g)
		#		{
		#			$varname = $1;
		#			$vartype = $2;
		#			$Globals::ENV{PRESCAN}->{PROC_VARS}->{$var_pos} = {VARNAME => $varname, VARTYPE => $vartype, DEFAULT => $default};
		#		}
		#	}
		#}
	}

	catalog_var_datatypes();
	$MR->log_msg("Prescan structure: " . Dumper($Globals::ENV{PRESCAN}));
	$MR->log_msg("USE_VARIABLE_QUOTE1: " . Dumper(\%USE_VARIABLE_QUOTE));
	
	$ret->{PRESCAN_INFO} = undef;
	return $ret;
}

sub mssql_preprocess
{
	my $lines = shift;

	my @stmts = preprocess_delimit_statements($lines, {keywords => [qw(BEGIN COMMIT)]});
	my $lines_string = join("\n", @stmts);

	my $comment = '[\s\n]*' . make_mask_match_regex('comment');

	# mark drop stmt preceding create temp table for possible special handling
	$lines_string =~ s|\bdrop[\s\n]+table[\s\n]+((?:if[\s\n]+exists[\s\n]+)?("?[\w0-9]+"?(?:\."?[\w0-9]+"?)*);(?:$comment)*[\s\n]*create[\s\n]+temp(?:orary)?[\s\n]+table[\s\n]+\2\b)|DROP __TEMP__ TABLE $1|gis;

	my @lines = split(/\n/, $lines_string);
	return @lines;
}

sub get_proc_var
{
	my $body = shift;
	my @vars = ();

	my @dec = split('DECLARE',$body);
	my $uc_vars = {};
	foreach my $x (@dec)
	{
		$x =~ s/^\s+|\s+$//g;
		if($x eq '')
		{
			next;
		}
		my $startPrentCount = 0;
		my $endPrentCount = 0;
		my $startIndex = 0;
		my $endIndex = 0;
		my $iterator = 1;
		my $prev_char='';
		my $single_quote_count = 0;
		my $duplicate_x = $x;
		foreach my $char (split('', $x))
		{
			if($char eq "'")
			{
				$single_quote_count += 1;
			}
			
			if($char eq '(')
			{
				$startPrentCount += 1;
			}
			
			if($char eq ')')
			{
				$endPrentCount += 1;
			}
			if($char eq ',')
			{
				if(($single_quote_count > 0 and !($single_quote_count & 1)) or $startPrentCount == $endPrentCount)
				{
					my $temp_str = substr($duplicate_x,0,$iterator-1);
					$temp_str =~ s/^\s+|\s+$//g;
					push(@vars,$temp_str);
					$duplicate_x = substr($duplicate_x,$iterator);
					$startIndex = 0;
					$iterator = 0;
					$single_quote_count =0;
					$startPrentCount = 0;
					$endPrentCount = 0;
				}
			}
			$iterator += 1;
		}
		push(@vars, $duplicate_x) unless grep{$_ eq $duplicate_x} @vars;
	}
	return @vars;
}

sub handle_named_exception
{
	my $ar = shift;
	my $str = join("\n", @$ar);
	$MR->log_msg("handle_named_exception INPUT:\n$str\n");
	my ($exc_name, $rest) = ('UNKNOWN_EXCEPTION','');
	my $ret = '';
	if ($str =~ /EXCEPTION\s+WHEN\s+(\w+)\s+THEN(.*)/gis)
	{
		($exc_name, $rest) = map { $MR->trim($_) } ($1,$2);
		$MR->log_msg("handle_named_exception: Exception name: $exc_name, Rest of the code: $rest");

		my $cat = '';
		$cat = $CONVERTER->categorize_statement($rest);
		$cat = '__DEFAULT_HANDLER__' if($cat eq '');
		$MR->log_msg("handle_named_exception: Rest category: $cat");
		my $handler = $CFG{fragment_handling}->{$cat};
		$MR->log_msg("handle_named_exception: fragment handling handler: $handler");
		my $eval_str = $handler . '([$rest]);';
		my $result = eval($eval_str);
		my $ret = $@;
		if ($ret)
		{
			$MR->log_error("************ EVAL ERROR: $ret ************");
		}
		else
		{
			$rest = $result;
			$EXCEPTIONS->{$exc_name}->{then} = $rest;
			$MR->log_msg("handle_named_exception: REST fragment converted: $rest");
			$LAST_EXCEPTION_NAME = $exc_name;
		}
	}
	return $ret;
}
sub handle_else_exception
{
	my $ar = shift;
	my $str = join("\n", @$ar);
	$MR->log_msg("handle_else_exception INPUT:\n$str\n");
	my $ret = end_procedure('} else {'); #call the normal end procedure
	$ret =~ s/\$\$/\}\n\$\$/gis; #plug in one more closing brace
	return $ret;
}
sub raise_application_error
{
	my $ar = shift;
	my $str = join("\n", @$ar);
	$MR->log_msg("raise_application_error INPUT:\n$str\n");
	$str =~ s/;\s*$//gis; #get rid of trailing semicolon
	my $expr = code_indent($MR->trim($CONVERTER->convert_sql_fragment($str)));

	$expr .= $STANDARD_CATCH_BLOCK;
	return $expr;
}

sub handle_raise_exception
{
	my $ar = shift;
	my $sql = join("\n", @$ar);
	$MR->log_msg("handle_raise_exception: $sql");
	my $exception_name = 'UNKNOWN_EXCEPTION';
	my $open_brace = '';
	if ($sql =~ /then\s+raise\s+(\w+)/gis)
	{
		$exception_name = $1;
		$open_brace = "$CFG{code_indent}\{\n";
	}
	return "$open_brace$CFG{code_indent}$CFG{code_indent}throw '$exception_name';";
}

sub convert_rais_error
{
	my $ar = shift;

	my $sql = join("\n", @$ar);
	#$sql =~ s/^\s*\;\s*$//gim;
	my @final = ();
	if($sql =~/\bRAISERROR\b\s*\((.*?)\,16\,1\)/gim)
	{
		my $text = $1;
		$text =~ s/^\s+|\s+$//g;
		$text =~ s/@/$VARIABLE_PREFIX/ig;
		my @match = $text =~ /$VARIABLE_PREFIX\w+/gim;
		foreach my $m (@match)
		{
			my $uc_val = uc($m);
			$text =~ s/\b$m\b/$uc_val/ig;
		}
		return "throw $text;";
	}
	return code_indent(join("\n", @final));
}
