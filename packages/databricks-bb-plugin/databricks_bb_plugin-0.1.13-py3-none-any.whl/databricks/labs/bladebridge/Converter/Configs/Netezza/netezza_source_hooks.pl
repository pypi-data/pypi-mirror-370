#snowflake javascript procedure generation
use strict;
use Globals;
use Data::Dumper;
use Common::MiscRoutines;
use DWSLanguage;

my $MR = new Common::MiscRoutines;
my $LAN = new DWSLanguage();
my %CFG = (); #entries to be initialized
my $CFG_POINTER = undef;
my $PRESCAN_CFG_POINTER = undef;
my $CONVERTER = undef;
my $INDENT = 0; #keep track of indents
my $INDENT_ENTIRE_SCRIPT = 0;
my $EXCEPTION_BLOCK = 'EXCEPTION_BLOCK';
my %SCRIPT_PARAMS_AND_VARS = ();
my %PRESCAN = ();
my $STMT_CNT = 0;
my $PROCEDURE_NAME = 'UNKNOWN_PROC';
my $FUNCTION_NAME = 'UNKNOWN_FUNCTION';
my %VARIABLES = (); #catch variables along the way
my %USE_VARIABLE_QUOTE = ();
my %CURSORS = ();
my $RETURN_TYPE = '';
my $USE_JS = 1;
my $IF_COUNT=0;
my $BEGIN_SEEN = 0;
my $STOP_OUTPUT = 0;
my %LAST_ASSIGNMENT = (); #keeps track of last assignments
my $EXCEPTIONS = {};
my $EXCEPTION_SEEN = 0; #flip when an exception is seen.  Used for constructing if/else if/else exception blocks
my $WITH_SEEN = 0;
my $LAST_WITH_NAME = '';
my $LAST_EXCEPTION_NAME = '';
my $UNDEFINED_WHILE_LOOPS = {};
my $UNDEFINED_WHILE_LOOP_SEEN = 0;
my $LAST_CURSOR_NAME = '';
my $procCount = 0;
my $LAST_ROWCOUNT_VAR = '';
my $MLOAD = undef;
my $PRESCAN_MLOAD = 0;
my $FILENAME = undef;
my %VAR_BEFORE_AFTER_CALL = ();
my $DOLLAR_PREFIX = '__DOLLAR__';
my @VAR_DEFAULT_VALUES = ();

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
		for(my $i=0; $i<$INDENT + $cfg_indents; $i++)
		{
			$spaces .= "\t";
		}
		$ln = $spaces . $ln;
	}
	return join("\n", @lines);
}

#netezza
sub prescan_code_netezza #gets called before init hooks
{
	my $content = shift;
	my @cont = @$content;
	
	#print "******** prescan_code netezza $filename *********\n";
	if(!$CFG_POINTER)
	{
		$CFG_POINTER = $Globals::ENV{CONFIG};
	}
	$MR->log_msg("CFG_POINTER BEFORE PRESCAN2: " . Dumper($CFG_POINTER));
	my $ret = {}; #hash to keep everything that needs to be captured
	#my @cont = $MR->read_file_content_as_array($filename);
	my $str_cont = join("\n", @cont);
	#$DB::single = 1;
	#$str_cont =~ s/\bALIAS\s+FOR\s+\$/ALIAS FOR \$/gis; # seen new lines betwee these tokens, lets make it one line
	#$DB::single = 1;
	# if (! open(IN, $filename) )
	# {
	# 	print OUT "Cannot open file $filename - $!\n";
	# 	return $ret;
	# }
	my $cnt = 0;
	$str_cont =~ s/(\w+)\s+alias\b\s+for\s+/$1 alias for /gis;  # seen new lines betwee these tokens, lets make it one line
	@cont = split(/\n/, $str_cont);
	#while (my $ln = <IN>)
	foreach my $ln (@cont)
	{
		$cnt++;
		if ($ln =~ /(.+)\s+ALIAS FOR \$(\d+)/i && ! ($ln =~ /^\s*\-\-/ ))
		{
			my ($arg, $pos) = ($1,$2);
			$arg =~ s/^\s+|\s+$//g;
			my @ar = split(/ /, $arg);
			$arg = $MR->trim($ar[-1]) if $#ar>0; #we may have DECLARE keyword in front
			print "Found Arg $arg at position $pos, line $cnt\n";
			$PRESCAN{ARG}->{$pos} = $MR->trim(uc($arg));
			$PRESCAN{ARG_NAME}->{$pos} = $MR->trim(uc($arg));
			push(@{$PRESCAN{PROC_ARGS}},{NAME=>$MR->trim(uc($arg)),DATA_TYPE => $CFG_POINTER->{default_data_type}});
			$VARIABLES{$PRESCAN{ARG_NAME}->{$pos}} = 1;
			#push(@{$PRESCAN_CFG_POINTER->{line_subst}}, {"from" => "\\\$$pos", "to" => $PRESCAN{ARG_NAME}->{$pos} } );
			push(@{$PRESCAN_CFG_POINTER->{line_subst}}, {"from" => "$DOLLAR_PREFIX$pos", "to" => $PRESCAN{ARG_NAME}->{$pos} } );
		}
		elsif($ln =~ /\:=.*\$(\d+)/)
		{
			my $pos = $1;
			my $arg = "PARAM_$pos";
			print "Found implicit arg $arg at position $pos, line $cnt\n";
			$PRESCAN{ARG}->{$pos} = $MR->trim(uc($arg));
			$PRESCAN{ARG_NAME}->{$pos} = $MR->trim(uc($arg));
			push(@{$PRESCAN{PROC_ARGS}},{NAME=>$MR->trim(uc($arg)),DATA_TYPE => $CFG_POINTER->{default_data_type}});
			#push(@{$PRESCAN_CFG_POINTER->{line_subst}}, {"from" => "\\\$$pos", "to" => $arg } );
			push(@{$PRESCAN_CFG_POINTER->{line_subst}}, {"from" => "$DOLLAR_PREFIX$pos", "to" => $arg } );
			$VARIABLES{$arg} = 1;
		}
		else #check if there are dollar vars referenced without direct assignments
		{
			my @vars = ( $ln =~ /\$(\d+)/g );
			foreach my $v (@vars)
			{
				my $pos = $v;
				my $arg = "PARAM_$pos";
				$MR->log_msg("Found direct arg references without assignments: $arg");
				#print "Found implicit arg $arg at position $pos, line $cnt\n";
				$PRESCAN{ARG}->{$pos} = $MR->trim(uc($arg));
				$PRESCAN{ARG_NAME}->{$pos} = $MR->trim(uc($arg));
				#push(@{$PRESCAN{PROC_ARGS}},{NAME=>$MR->trim(uc($arg)),DATA_TYPE => $CFG_POINTER->{default_data_type}});
				#push(@{$PRESCAN_CFG_POINTER->{line_subst}}, {"from" => "\\\$$pos", "to" => $arg } );
				push(@{$PRESCAN_CFG_POINTER->{line_subst}}, {"from" => "$DOLLAR_PREFIX$pos", "to" => $arg } );
				$VARIABLES{$arg} = 1;
			}
		}
	}
	#close(IN);

	$MR->log_msg("Prescan structure: " . Dumper(\%PRESCAN));
	$ret = {PRESCAN_INFO => \%PRESCAN};

	#added on 9/21/2021 - scan for vars
	#my $cont = $MR->read_file_content($filename);
	$MR->log_msg("Check 001");
	if ($str_cont =~ /(CREATE|REPLACE)\s+PROCEDURE\s+([\w|\.]+)(.*?)\((.*)\).*RETURNS\s+(\w*).*NZPLSQL\b/gis)
	{
		my $proc = $2;
		$PRESCAN{PROC_NAME} = $proc;
		my $proc_args = $MR->trim($4);
		$RETURN_TYPE = $MR->trim($5);
		$MR->log_msg("Found proc args for $proc: $proc_args. Returns: $RETURN_TYPE");
		my @proc_args = map { $MR->trim($_) } split(/,/, $proc_args);
		my $pos = 0;
		foreach my $pa (@proc_args)
		{
			$pos++;
			#$pa =~ s/\[\]//gis; #get rid of []
			$PRESCAN{ARG}->{$pos} = $pa;
			my @tmp = split(/ /, $pa);
			my $arg_name = shift(@tmp);
			my $arg_type = join(' ', @tmp);
			#$arg_type =~ s/\[\]//gis; #get rid of []
			#$PRESCAN{ARG_NAME}->{$pos} = uc($arg_name);
			$PRESCAN{ARG_TYPE}->{$pos} = $PRESCAN{ARG}->{$pos};
		}
	}
	elsif($str_cont =~ /\bCREATE\s+\bOR\b\s+REPLACE\s+PROCEDURE\s+([\w|\.]+)(.*?)\((.*)\).*RETURNS\s+(\w*).*NZPLSQL\b/gis)
	{
		my $proc = $1;
		$PRESCAN{PROC_NAME} = $proc;
		my $proc_args = $MR->trim($3);
		$RETURN_TYPE = $MR->trim($4);
		$MR->log_msg("Found proc args for $proc: $proc_args. Returns: $RETURN_TYPE");
		my @proc_args = map { $MR->trim($_) } split(/,/, $proc_args);
		my $pos = 0;
		foreach my $pa (@proc_args)
		{
			$pos++;
			#$pa =~ s/\[\]//gis; #get rid of []
			$PRESCAN{ARG}->{$pos} = $pa;
			my @tmp = split(/ /, $pa);
			my $arg_name = shift(@tmp);
			my $arg_type = join(' ', @tmp);
			#$arg_type =~ s/\[\]//gis; #get rid of []
			#$PRESCAN{ARG_NAME}->{$pos} = uc($arg_name);
			$PRESCAN{ARG_TYPE}->{$pos} = $PRESCAN{ARG}->{$pos};
		}		
	}
	
	if ($content =~ /BEGIN_PROC(.*?)\bDECLARE\b(.*?)\bBEGIN\b/gis)
	{
		my $decl = $2;
		$MR->log_msg("DECLARE Block found: $2");
		my @vars = map {$MR->trim($_)} split(/\;/, $decl);
		foreach my $v (@vars)
		{
			my @ar = split(/\s+/,$v);
			my $var_name = $ar[0];
			next unless $var_name;
			$VARIABLES{$var_name} = 1;
			if ($v =~ /constant.*\:\s*=(.*)/gis)
			{
				my $value = $MR->trim($1);
				push(@VAR_DEFAULT_VALUES, "const " . uc($var_name) . " = $value");
			}
			elsif ($v =~ /.*\:\s*=(.*)/gis)
			{
				my $value = $MR->trim($1);
				push(@VAR_DEFAULT_VALUES, uc($var_name) . " = $value");
			}
		}
		$MR->log_msg("Variables found: " . Dumper(\%VARIABLES));
		$MR->log_msg("Default var values found: " . Dumper(\@VAR_DEFAULT_VALUES));
	}

	$MR->log_msg("PRESCAN_STRUCT: " . Dumper(\%PRESCAN));
	$MR->log_msg("CFG_POINTER AFTER PRESCAN: " . Dumper($CFG_POINTER));
	$Globals::ENV{PRESCAN} =  \%PRESCAN;
	$MR->log_msg("CFG_POINTER AFTER PRESCAN_12: " . Dumper($Globals::ENV{PRESCAN}));

	return $ret;
}

sub netezza_preprocess
{
	my $cont = shift; #pointer to array
	$MR->log_msg("Preprocessing netezza file");
	my $cont_str = join("\n",@$cont);
	#get rid of the declare section.
	if ($cont_str =~ /BEGIN_PROC(.*?)\bDECLARE\b(.*?)\bBEGIN\b/gisp)
	{
		my ($prematch, $match, $postmatch) = (${^PREMATCH}, ${^MATCH}, ${^POSTMATCH});
		$cont_str = "$prematch\nBEGIN_PROC;\n$postmatch";
		$MR->log_msg("DECLARE Block found. Removing: $2");
	}

	$cont_str =~ s/\$(\d+)/$DOLLAR_PREFIX$1/gis;
	#handle bad formatting
	$cont_str =~ s/AUTOCOMMIT\s+(ON|OFF)\s+(\S)/AUTOCOMMIT $1;\n$2/gis;
	$cont_str =~ s/(for\s+\w+)\s+in\s*\n\s*(select)/$1 in $2/gis;
	$cont_str =~ s/\bLOOP\b\s+IF\b/\nLOOP\nIF/gi;
	$cont_str =~ s/LOOP\s*$/LOOP;/gim; #multi line flag
	$cont_str =~ s/END\s*\n\s*IF\s*;/\nEND IF;\n/gis;
	$cont_str =~ s/; *END\s*IF;/;\nEND IF;\n/gis; # if "END IF" is on the same line as preceeding statement, move it to the next line
	$cont_str =~ s/END\s*\n\s*LOOP\s*;/\nEND LOOP;\n/gis;
	$cont_str =~ s/; *END\s*LOOP;/;\nEND LOOP;\n/gis; # if "END LOOP" is on the same line as preceeding statement, move it to the next line
	$cont_str =~ s/;\s*ELSE/;\nELSE/i;
	$cont_str =~ s/;END/;\nEND/i;
	
	$cont_str =~ s/END\s+PROC\;?/END_PROC;/gi;
	$cont_str =~ s/^(?!\s*\-\-)(.*)\'\s*\;/$1\n';\n/gm;
	$cont_str =~ s/^(?!\s*\-\-)(.*)\)\s*\;/$1\n);\n/gm;
	$cont_str =~ s/RETURN\s+TRUE/return true/g;
	$cont_str =~ s/RETURN\s+FALSE/return false/g;
	$cont_str =~ s/\bTHEN\b/\nTHEN/gi;

	my @ret = split(/\n/, $cont_str);
	$MR->log_msg("PREPROCESSED CONTENT:\n" . join("\n", @ret) . "\n***** END OF CONTENT ****");

	return @ret;
}

sub handle_begin
{
	$BEGIN_SEEN = 1;
	$procCount++;
	return code_indent("//BEGIN");
}

sub handle_end
{
	#$BEGIN_SEEN = 1;
	#$procCount++;
	return code_indent("//END");
}

sub init_hooks #register this function in the config file
{
	my $param = shift;
	%CFG = %{$param->{CONFIG}};
	$CFG_POINTER = $param->{CONFIG}; #give the ability to modify config incrementally
	if ($PRESCAN_CFG_POINTER && $PRESCAN_CFG_POINTER->{line_subst})
	{
		$MR->log_msg("PRESCAN_CFG_POINTER ASSIGNMENT: " . Dumper($PRESCAN_CFG_POINTER));
		foreach my $k (@{$PRESCAN_CFG_POINTER->{line_subst}})
		{
			push(@{$CFG_POINTER->{line_subst}}, $k);
		}
	}

	$MR->log_msg("CFG_POINTER BEFORE PRESCAN: " . Dumper($CFG_POINTER));
	$CONVERTER = $param->{CONVERTER};
	$MLOAD = $param->{MLOAD};
	$MR->log_msg("INIT_HOOKS Called. config:\n" . Dumper($CFG_POINTER));

	$MLOAD->process_file($FILENAME) if $PRESCAN_MLOAD && $MLOAD;

	#Reinitilize vars for when -d option is used:
	$INDENT = 0; #keep track of indents
	%PRESCAN = ();
	$STMT_CNT = 0;
	$PROCEDURE_NAME = 'UNKNOWN_PROC';
	$FUNCTION_NAME = 'UNKNOWN_FUNCTION';
	%VARIABLES = (); #catch variables along the way
	#%USE_VARIABLE_QUOTE = ();
	%CURSORS = ();
	$RETURN_TYPE = '';
	$USE_JS = 1;
	$IF_COUNT=0;
	$BEGIN_SEEN = 0;
	$STOP_OUTPUT = 0;
	%LAST_ASSIGNMENT = (); #keeps track of last assignments
	$EXCEPTIONS = {};
	$EXCEPTION_SEEN = 0; #flip when an exception is seen.  Used for constructing if/else if/else exception blocks
	$WITH_SEEN = 0;
	$LAST_WITH_NAME = '';
	$LAST_EXCEPTION_NAME = '';
	$UNDEFINED_WHILE_LOOPS = {};
	$UNDEFINED_WHILE_LOOP_SEEN = 0;
	$LAST_CURSOR_NAME = '';
	$procCount = 0;
	$LAST_ROWCOUNT_VAR = '';
	$Globals::ENV{CONFIG} = $param->{CONFIG};
	$Globals::ENV{CONFIG}->{FILENAME} = $FILENAME;	
}


sub init_hooks_keep_prescan #register this function in the config file
{
	my %tmp1 = %PRESCAN;
	my %tmp2 = %VARIABLES;
	my $tmp_CFG_POINTER = $CFG_POINTER;
	init_hooks(@_);
	%PRESCAN = %tmp1;
	%VARIABLES = %tmp2;
	$CFG_POINTER = $tmp_CFG_POINTER;

}

sub create_procedure_from_netezza
{
	my $ar = shift;
	my $str = join("\n", @$ar);
	$MR->log_msg("Entering create_procedure_from_netezza");

	my $proc_name = 'UNKNOWN_PROC';
	if ($str =~ /PROCEDURE\s+(\w+)/is)
	{
		$proc_name = $1;
	}
	elsif ($str =~ /FUNCTION\s+(\w+)/is)
	{
		$proc_name = $1;
	}
	my @arg_types = ();
	if ($str =~ /PROCEDURE\s+\w+\((.*)\)\s*RETURNS/is)
	{
		@arg_types = split(/\,/, $1);
		print "ARG TYPES: " . join(",", @arg_types) . "\n";
	}

	$MR->log_msg("Starting procedure creation from netezza, proc name: $proc_name, args: " . Dumper($PRESCAN{ARG}));

	#my $mr = new Common::MiscRoutines();
	my @args = ();

	if ($PRESCAN{ARG})
	{
		my $arg_cnt = 0;
		foreach my $pos (sort {$a <=> $b} keys %{$PRESCAN{ARG}})
		#(sort {$PRESCAN{ARG}->{$a} <=> $PRESCAN{ARG}->{$b}} keys %{$PRESCAN{ARG}})
		{
			$MR->log_msg("Adding arg $PRESCAN{ARG}->{$pos}, pos $pos");
			#my $arg_type = $arg_types[$arg_cnt];
			#$arg_type = 'varchar' if ! $arg_type or lc($arg_type) eq 'varargs' or lc$arg_type =~ /CHARACTER VARYING/i;
			#$arg_type = 'float' if $arg_type =~ /INT/i;
			my $arg_type = convert_datatype($PRESCAN{ARG_TYPE}->{$pos});
			assign_var_before_after_call($PRESCAN{ARG_NAME}->{$pos}, $arg_type);
			push(@args, "$PRESCAN{ARG_NAME}->{$pos} $arg_type");
			$arg_cnt++;
		}
	}

	my $var_with_values='';
	if ($#VAR_DEFAULT_VALUES >= 0)
	{
		$var_with_values = "\n" . join("\n", map {"\t$_"} @VAR_DEFAULT_VALUES) . "\n";
	}

	my $decl = "CREATE OR REPLACE PROCEDURE $proc_name\n(\n" . join(",\n", map {"  $_"} @args) . 
		"\n)\nreturns variant\nlanguage javascript\nas\n\$\$\ntry {$var_with_values\n$CFG{standard_proc_vars}";
	$PROCEDURE_NAME = $proc_name;
	return $decl;
}

#**************************Converting functions*******************************

sub convert_datatype
{
	my $dt = shift;
	my $ret = "$dt /* data type not mapped in datatype_mapping section */";
	if ($CFG{datatype_mapping})
	{
		foreach my $k (keys %{$CFG{datatype_mapping}})
		{
			return $CFG{datatype_mapping}->{$k} if $dt =~ /$k/i;
		}
	}
	return $CFG{default_procedure_arg_datatype} || $ret;
}

sub convert_cursor
{
	my $ar = shift;
	my $str = join("\n", @$ar);
	my $sql = '';

	if($str =~ /CURSOR\s+(.*?)\s+IS\s*$/is)
	{
		my $cursor_name = $1;
		$CURSORS{$cursor_name} = 1;
		$LAST_CURSOR_NAME = $cursor_name;
	}
	elsif($str =~ /CURSOR\s+(.*?)\s+IS\s+(.*?);/is)
	{
		my $cursor_name = $1;
		$CURSORS{$cursor_name} = 1;
		$sql = JS_substitute({
		SQL => $2,
		CURSOR_NAME => $cursor_name,
		TEMPLATE => 'cursor_create'
		});
	}

	return code_indent($sql);
}

sub handle_exception_init
{
	my $ar = shift;
	my $str = join("\n", @$ar);
	$MR->log_msg("handle_exception_init INPUT:\n$str\n");

	if($str =~ /PRAGMA\s+EXCEPTION_INIT\s*\((.*?)\s*,\s*(.*?)\)/i)
	{
		my $exception_name = $1;
		my $exception_code = $2;
		$EXCEPTIONS->{$exception_name}->{code} = $exception_code;
	}
	return '';
}

sub handle_when_then
{
	my $ar = shift;
	return '' if $STOP_OUTPUT;
	my $str = join("\n", @$ar);
	$MR->log_msg("handle_when_then INPUT:\n$str\n");

	$LAST_EXCEPTION_NAME = '';
	my $ret = '';
	if($str =~ /WHEN\s+(\w+)\s+THEN(.*)/gis)
	{
		my ($when, $then) = map { $MR->trim($_) } ($1,$2);
		$MR->log_msg("handle_when_then: When: $when, Then: $then");

		my $cat = '';
		$cat = $CONVERTER->categorize_statement($then);
		$cat = '__DEFAULT_HANDLER__' if($cat eq '');
		$MR->log_msg("handle_when_then: Then category: $cat");

		my $handler = $CFG{fragment_handling}->{$cat};
		$MR->log_msg("handle_when_then: fragment handling handler: $handler");
		my $eval_str = $handler . '([$then]);';
		$then = eval($eval_str);

		my $return = $@;
		if ($return)
		{
			$MR->log_error("************ EVAL ERROR: $return ************");
		}
		else
		{
			if($EXCEPTION_SEEN)
			{
				$when = uc($when) if(uc($when) eq 'OTHERS');
				$EXCEPTIONS->{$when}->{then} = $then;
				$LAST_EXCEPTION_NAME = $when;
			}
			$MR->log_msg("handle_when_then: Then fragment converted: $then");
		}
	}
	return $ret;
}

sub handle_named_exception
{
	my $ar = shift;
	return '' if $STOP_OUTPUT || !$USE_JS;
	my $str = join("\n", @$ar);
	$MR->log_msg("handle_named_exception INPUT:\n$str\n");
	my ($exc_name, $rest) = ('UNKNOWN_EXCEPTION','');
	my $ret = '';
	if ($str =~ /EXCEPTION\s+WHEN\s+(\w+)\s+THEN(.*)/gis)
	{
		($exc_name, $rest) = map { $MR->trim($_) } ($1,$2);
		$MR->log_msg("handle_named_exception: Exception name: $exc_name, Rest of the code: $rest");

		$EXCEPTION_SEEN = 1;

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
	$STOP_OUTPUT = 1;
	return $ret;
}

sub raise_application_error
{
	my $ar = shift;
	return '' if $STOP_OUTPUT;
	my $str = join("\n", @$ar);
	$MR->log_msg("raise_application_error INPUT:\n$str\n");
	$str =~ s/;\s*$//gis; #get rid of trailing semicolon
	my $expr = code_indent($MR->trim($CONVERTER->convert_sql_fragment($str)));

	$expr .= $STANDARD_CATCH_BLOCK;
	return $expr;
}

sub end_procedure_no_more_output
{
	$MR->log_msg("end_procedure_no_more_output called. Args: " . Dumper(\@_));
	$STOP_OUTPUT = 1;
	return end_procedure();
}

sub end_procedure
{
	my $first_line = shift;
	my $ref = ref($first_line);
	$first_line = '' if $ref eq 'ARRAY';
	$MR->log_msg("end_procedure called. First line type: $ref, First line:  '$first_line'");

	if(!$USE_JS)
	{
		if($STOP_OUTPUT == 1)
		{
			return '';
		}
		$STOP_OUTPUT = 1;
		return "\n\$\$";
	}

	$first_line = '} catch (err) {' unless $first_line;
	my $add_sql = '';
	if ($PRESCAN{SETOF} && !$PRESCAN{SETOF_RETURN_EXECUTED})
	{
		$add_sql = code_indent(convert_return([])) . "\n";
	}

	$LAST_EXCEPTION_NAME='';
	if(!$EXCEPTIONS->{OTHERS} || $EXCEPTIONS->{OTHERS}->{then} eq '')
	{
		$EXCEPTIONS->{OTHERS}->{then} = $STANDARD_CATCH_BLOCK;
	}

	if(keys($EXCEPTIONS)>0)
	{
		my $temp='';
		my $codes='';
		my $other = '';

		#Form catch statement
		$INDENT--;
		my $catch = "\n}\ncatch (err)\n{";
		$catch = code_indent($catch) . "\n";
		$INDENT+=2;

		foreach my $key (keys($EXCEPTIONS))
		{
			my $exc = $EXCEPTIONS->{$key};
			next if(!$exc->{then});

			if(uc($key) eq "OTHERS")
			{
				#Strip extra white space if standard catch block
				if($exc->{then} eq $STANDARD_CATCH_BLOCK)
				{
					#$exc->{then} =~ s/\n\s+/\n/g;
					#$exc->{then} =~ s/^\n//g;
					$temp = $MR->trim($exc->{then});
					$INDENT--;
					$other .= code_indent($temp) . "\n";
					$INDENT++;
				}
				else
				{
					$temp = $exc->{then};
					$INDENT--;
					$other .= code_indent($MR->trim($temp)) . "\n\n" . code_indent($MR->trim($STANDARD_CATCH_BLOCK)) . "\n";
					$INDENT++;
				}
			}

			if($exc->{code})
			{
				$temp = "if(err['code'] == $exc->{code})\n{";
				$codes .= code_indent($temp) . "\n";
				$INDENT++;

				$temp = $exc->{then};

				$codes .= code_indent($temp) . "\n";
				$INDENT--;
				$codes .= code_indent("}") . "\n";
			}
		}

		$INDENT--;
		if($codes ne '')
		{
			$codes = code_indent("if(typeof(err) == 'object')\n{") . "\n" . $codes;
			$codes .= code_indent("}") . "\n";
		}

		my $ret = $catch . $codes . "\n";
		$ret .= code_indent($MR->trim($STANDARD_CATCH_BLOCK)) . "\n";
		$INDENT--;
		#$ret .= $other;
		$STOP_OUTPUT = 1;
		return $ret . "}\n\$\$";
	}
	$STOP_OUTPUT = 1;
	return $add_sql . $first_line . $STANDARD_CATCH_BLOCK . '
}
$$';

}

sub handle_begin_autocommit
{
	return "/* Removed autocommit statement */";
}

sub handle_exception
{
	return "/* Removed exception handling - using catch-all block at the end of procedure */";
}


sub convert_comment
{
	my $ar = shift;
	foreach (@$ar)
	{
		$_ =~ s/^\s*\-\-/\/\//;
	}
	map {$_ = '' . $_} @$ar; #return as is, no prefixes required.
	return code_indent(join("\n", @$ar));
}

sub convert_var_declare
{
	my $ar = shift;
	my @final = ();
	#my %subst = ('\|\|' => '+');
	$MR->log_msg("convert_var_declare: " . Dumper($ar));
	my $tmp_cont = join("\n", @$ar);
	if ($tmp_cont =~ /^\s*CREATE.*PROCEDURE/) #we accidentally got here. reroute to proc creation routine
	{
		$MR->log_msg("convert_var_declare: routing to create_procedure_from_netezza");
		return create_procedure_from_netezza($ar);
	}

	push(@final,"$CFG{inline_comment_start}/* Commented variables, no need to define them */");

	foreach my $x (@$ar)
	{
		$x = $MR->trim($x);
		if ($x eq '')
		{
			push(@final,"");
			next;
		}
		next if $x =~ /^\s*declare\s*$/i; #empty declare line

		push(@final,"$CFG{inline_comment_start}$x");
		next;
		#no need to initialize vars


		my $tmp = (split(/ /, $x))[0];
		my $value = 'None';

		if ($x =~ /\:\=(.*)/)
		{
			$value = adjust_expr($MR->trim($1));
		}
		my $final = "$tmp = $value";
		$SCRIPT_PARAMS_AND_VARS{$tmp} = 1;
		#map {$final =~ s/$_/$subst{$_}/g} keys %subst;
		push(@final, $final);
	}
	return code_indent(join("\n", @final));
}

sub no_SELECT_prefix #check if an assignment needs to have SELECT in front
{
	my $expr = shift;
	my @kw = qw(SELECT UPDATE CREATE DELETE INSERT RAISE MERGE DROP);
	foreach my $kw (@kw)
	{
		return 1 if ($expr =~ /^\s*['|]\s*$kw\s/gis);
	}
	return 0;
}


sub convert_assignment
{
	my $ar = shift;
	$MR->log_msg("convert_assignment_greenplum: " . Dumper(\%SCRIPT_PARAMS_AND_VARS));
	my $sql = join("\n", @$ar);
	$MR->log_msg("convert_assignment_greenplum: SQL: $sql\nCURSORS: " . Dumper(\%CURSORS));
	$sql =~ s/\;$//;
	my $quote_escape_str = $LAN->get_quote_escape_str();
	my $curr_varname = '';
	my $curr_expr = '';
	delete $VARIABLES{''}; #delete variables with empty names
	my @additional_vars = (); #in case we have a multi var assignment
	my $multi_var_flag = 0;

	if ($sql =~ /(select.*)into\s+(\w+)(.*)/gis) #select ZZZ into var FROM ... WHERE ..
	{
		my ($before, $var_name, $after) = map {$MR->trim($_)} ($1, $2, $3);
		$var_name = uc($var_name);
		$MR->log_msg("convert_assignment_greenplum: VARIANT 2: $sql\nBEFORE: $before\nAFTER: $after\nVARNAME: $var_name");
		my $cnt = 0;
		while($after =~ /^\s*,\s*(\w+)\b(.*)/is)
		{
			my $add_var = uc($MR->trim($1));
			$after = $2;
			$MR->log_msg("Additional var found in multi var assignment: $add_var ***** AFTER: $after");
			push(@additional_vars, $add_var);
			$VARIABLES{$add_var} = 1;
			$multi_var_flag = 1;
			last if $cnt++ >= 50;
		}
		unshift(@additional_vars, $var_name) if $multi_var_flag;
		$after = $MR->trim($after);
		$sql = "$var_name := $before $after";
		$VARIABLES{$var_name} = 1;
		$VARIABLES{uc($var_name)} = 1;
		$curr_varname = $var_name;
		$curr_expr = $MR->trim("$before $after");
	}
	elsif ($sql =~ /(.*)into\s+(\w+)(.*)/is && ! ($sql =~ /\:\=/) &&  ($sql =~ /select(.*)into/gis)) #select ZZZ into var
	{

		my ($before, $var_name, $after) = map {$MR->trim($_)} ($1, $2, $3);
		$var_name = uc($var_name);
		$MR->log_msg("convert_assignment_greenplum: VARIANT 3: $sql");
		#my $tmp = adjust_expr("$before $after");

		$sql = "$var_name := $before $after";
		$VARIABLES{$var_name} = 1;
		$curr_varname = $var_name;
		$curr_expr = $MR->trim("$before $after");
	}
	elsif ($sql =~ /(.*):=(.*)/gis) #just an assignment
	{
		($curr_varname, $curr_expr) = map { $MR->trim($_) } ($1,$2);
		$curr_varname = uc($curr_varname);
		$MR->log_msg("convert_assignment_greenplum: VARIANT 4: $sql");
		$curr_expr = refactor_statement_if_required($curr_expr);
	}
	elsif ($sql =~ /(.*?)=(.*)/gis) #just an assignment
	{
		($curr_varname, $curr_expr) = map { $MR->trim($_) } ($1,$2);
		$curr_varname = uc($curr_varname);
		$MR->log_msg("convert_assignment_greenplum: VARIANT 5: $sql");
	}

	my $non_sql = 0; #indicates if we need SQL engine or not
	if ($CFG{non_sql_assignment}) # check if the expression can be handled by javascript directly, and not in SQL
	{
		foreach my $pat (@{$CFG{non_sql_assignment}})
		{
			if ($curr_expr =~ /$pat/is)
			{
				$MR->log_msg("Expression is NON-SQL, can be handled in Javascript");
				$non_sql = 1;
				last;
			}
		}
	}
	if ($CFG{forced_sql_assignment})
	{
		foreach my $pat (@{$CFG{forced_sql_assignment}})
		{
			if ($curr_expr =~ /$pat/is)
			{
				$MR->log_msg("Expression is FORCED-SQL, has to be handled in SQL");
				$non_sql = 0;
				last;
			}
		}
	}

	$MR->log_msg("Non-SQL flag: $non_sql");

	if ($MR->is_string_literal($curr_expr) || $MR->is_number($curr_expr))
	{
		$MR->log_msg("Expression is a constant. Literal: " . $MR->is_string_literal($curr_expr));
		if ($curr_expr =~ /^'(.*)'$/s)
		{
			$curr_expr = '`' . $1 . '`'; #multiline support
			$curr_expr =~ s/'$/`/s;
			$curr_expr =~ s/''/'/gs;
		}
		$curr_varname = uc($curr_varname);
		$sql = $curr_varname . ' = ' . $MR->trim($CONVERTER->convert_sql_fragment($curr_expr));
		#if ($MR->is_string_literal($curr_expr)) #get rid of two consecutive single quotes and change surrounding quotes to backticks
		#{
			#$MR->log_msg("Changing quotes");
			#$curr_expr =~ s/^'/`/s;

		#}
		#$MR->trim($curr_expr);
		$VARIABLES{$curr_varname} = 1;
	}
	elsif (!$non_sql) #SQL expression
	{
		my $expr = $curr_expr;

		$LAN->set_sql_mode(1);
		my @tok = $LAN->split_expression_tokens($expr);
		#$MR->debug_msg("TOKENS AFTER SQL MODE SPLIT: " . Dumper(\@tok));
		my @tok_classes = $LAN->classify_tokens(@tok);
		$LAN->set_sql_mode(0);

		my $func_call_cnt = 0;
		foreach my $x (@tok_classes)
		{
			$func_call_cnt++ if $x->{TYPE} eq 'FUNCTION';
			$x->{TOKEN} = '+' if $x->{TOKEN} eq '||'; #change concat operator
		}

		my $reassembled_expr = join(' ', map {$_->{TOKEN}} @tok_classes);
		$reassembled_expr =~ s/$quote_escape_str//gis; #get rid of escaping that was plugged in by the language processor

		if ($func_call_cnt == 0 && ! $expr =~ /^\s*SELECT/is)
		{
			$MR->log_msg("convert_assignment: VARIANT 202. Expression contains no function calls and is not a SELECT statement. Eligible for simple JS assignment: $reassembled_expr\n TOKENS: " . Dumper(\@tok_classes));
			$curr_varname = uc($curr_varname);
			$sql = $curr_varname . ' = ' . $MR->trim($reassembled_expr);
			$VARIABLES{$MR->trim($curr_varname)} = 1;
		}
		else
		{
			#$expr = $MR->trim($CONVERTER->convert_sql_fragment($expr));
			my $no_SELECT_prefix = no_SELECT_prefix($expr);
			$MR->log_msg("Expression is not a constant. no_SELECT_prefix: $no_SELECT_prefix. ***$expr***");
			$expr = "SELECT $expr" unless $expr =~ /^SELECT/i; #unless $no_SELECT_prefix; #
			#$VARIABLES{$ar[0]} = 1;
			$curr_varname = $MR->trim(uc($curr_varname));
			$VARIABLES{$MR->trim($curr_varname)} = 1;
			$sql = JS_substitute({
				VAR => $curr_varname,
				SQL => $expr,
				TEMPLATE => $multi_var_flag?'multi_var_assignment_wrapper':'var_assignment_wrapper'
				});
			if ($#additional_vars >= 0)
			{
				$MR->log_msg("Adding var assignment template for multi var assignment: " . Dumper(\@additional_vars));
				my $col_cnt = 0;
				$STMT_CNT--; #decrement it, because js_substitute increments this var
				foreach my $v (@additional_vars) # multi variable assignment
				{
					$col_cnt++;
					my $var_assign_sql = JS_substitute({
						VAR => $v,
						COLUMN_NUMBER => $col_cnt,
						NO_SQL_PROCEED => 1,
						TEMPLATE => 'multi_var_assignment_statement'
						});
					$sql .= $var_assign_sql . "\n";
				}
				$STMT_CNT++; #increment it back
			}
		}
	}
	else #it is a non-sql assignment
	{
		#my @tok = $LAN->split_expression_tokens($sql);
		$curr_varname = uc($curr_varname);
		$curr_expr = convert_sql_expression_to_javascript($curr_expr);
		$curr_expr =  $MR->trim($CONVERTER->convert_sql_fragment($curr_expr, {STATEMENT_CATEGORY => 'JAVASCRIPT'}));
		my $comment = '';
		if ($curr_expr =~ /^\/\*(.*)/gis) #this is a commented code
		{
			$curr_expr = $1;
			$comment = '/*';
		}
		$sql = "$comment$curr_varname" . ' = ' . $MR->trim($curr_expr);
		$VARIABLES{$curr_varname} = 1;
		$LAST_ASSIGNMENT{$curr_varname} = $MR->trim($curr_expr);
	}
	#$sql =~ s/\:\=/=/gis;
	#$sql = adjust_expr($sql);

	delete $VARIABLES{''}; #delete variables with empty names
	$MR->log_msg("convert_assignment_greenplum END VARS: " . Dumper(\%VARIABLES));

	return code_indent(var_upcase($sql));
	#return plug_indent($MR->trim($sql));
}

sub netezza_convert_assignment
{
	my $ar = shift;
	#return '' if $STOP_OUTPUT;
	my $sql = join("\n", @$ar);
	$MR->log_msg("netezza_convert_assignment: " . Dumper(\%SCRIPT_PARAMS_AND_VARS) . "\nSQL: $sql");

	my @ar = map {$MR->trim($_)} split(/\:\s*\=/, $sql) if $sql =~ /\:\s*\=/gis;
	my $var = $ar[0];
	my $expr = $ar[1];
	if ($#ar < 0) #no tokens found, try matching on the equal sign without the colon
	{
		$MR->log_msg("netezza_convert_assignment: Trying without colon.");
		if ( $sql =~ /(.*?)\s*(=)(.*)/gis )
		{
			($var, $expr) = ($1, $3);
			$MR->log_msg("netezza_convert_assignment: Got var $var.");
		}
		else
		{
			$MR->log_msg("netezza_convert_assignment: Could not parse assignment! $sql");
		}
	}
	
	$expr =~ s/;\s*$//gis;


	$MR->log_msg("convert_assignment: VARIANT 20. Expression contains no function calls. Eligible for simple JS assignment: $expr\n");
	$MR->log_msg("convert_assignment: LINE_SUBST: " . Dumper($CONVERTER->{CONFIG}->{line_subst}));

	$expr = $MR->trim($CONVERTER->convert_sql_fragment($expr));
	$expr = "SELECT $expr" unless $expr =~ /^\s*SELECT/gis;
	$expr = JS_substitute({
		VAR => uc($var),
		SQL => $expr,
		TEMPLATE => 'var_assignment_wrapper'
		});
	$var = uc($var);
	$sql = $MR->trim($expr);
	#$sql = $ar[0] . ' = ' . $MR->trim($reassembled_expr);
	#$VARIABLES{$MR->trim($ar[0])} = 1;

	#$sql =~ s/;\s*$//gis;

	#return code_indent($sql) if($sql =~ /;\s*$/);
	return code_indent($sql."\n\n");
}

sub convert_dml
{
	my $ar = shift;
	return '' if $STOP_OUTPUT;
	my $sql = join("\n", @$ar);
	
	if(!$USE_JS)
	{
		my $ret = $CONVERTER->convert_sql_fragment($MR->trim($sql));
		$ret = code_indent($ret);
		$ret =~ s/;\s*$//;
		$ret .= "\n" . $MR->trim(end_procedure());
		return $ret;
	}

	$sql =~ s/\;$//;
	$sql =~ s/^\s+//g;

	$MR->log_msg("convert_dml ORIG:\n$sql");

	if($LAST_CURSOR_NAME ne '')
	{

		$sql = JS_substitute({
		SQL => $sql,
		CURSOR_NAME => $LAST_CURSOR_NAME,
		TEMPLATE => 'cursor_create'
		});
		$LAST_CURSOR_NAME = '';
	}
	else
	{
		$sql = JS_substitute({
		SQL => $sql,
		TEMPLATE => 'dml_wrapper'
		});
	}

	$sql = var_upcase($sql);
	$MR->log_msg("convert_dml CONVERTED:\n$sql");

	if($LAST_EXCEPTION_NAME ne '')
	{
		$EXCEPTIONS->{$LAST_EXCEPTION_NAME}->{then}.=$sql;
		return '';
	}
	return code_indent($sql);

	#$sql = adjust_expr($sql);
	#my $quote = "'";
	#$quote = '"""' if $sql =~ /\n/; #change quotes to triple quotes if the statement contains newlines
	#return plug_indent("$CFG{rowcount_varname} = $CFG{dbh_varname}.exec($quote$sql$quote)");
}

sub handle_dynamic_sql
{
	my $ar = shift;
	return '' if $STOP_OUTPUT;
	my $sql = join("\n", @$ar);
	$MR->log_msg("handle_dynamic_sql: $sql");
	if ($sql =~ /EXECUTE\s+IMMEDIATE\s(.*)/gis)
	{
		$sql = $1;
	}
	if ($sql =~ /EXECUTE\s+(.*)/gis)
	{
		$sql = $1;
	}
	$sql =~ s/\;$//;
	$sql =~ s/^\s+//g;
	$sql =~ s/^'//;
	$sql =~ s/'$//;

	$sql = JS_substitute({
		SQL => $sql,
		TEMPLATE => 'dml_wrapper'
		});
	
	if($LAST_EXCEPTION_NAME ne '')
	{
		$EXCEPTIONS->{$LAST_EXCEPTION_NAME}->{then}.=$sql;
		return '';
	}
	return code_indent($sql);

	#$sql = adjust_expr($sql);

	#my $quote = "'";
	#$quote = '"""' if $sql =~ /\n/; #change quotes to triple quotes if the statement contains newlines
	#return plug_indent("$CFG{rowcount_varname} = $CFG{dbh_varname}.exec($sql)");
}


sub convert_return
{
	my $ar = shift;
	return '' if $STOP_OUTPUT;
	my $sql = join("\n", @$ar);

	my $comment = '';
	if($sql =~ /(\/\*.*?\*\/)/)
	{
		$comment = $1;
		$sql =~ s/\/\*.*?\*\///;
	}
	elsif($sql =~ /^\s*RETURN\s*;\s*$/i)
	{
		return code_indent("return \"\";");
	}

	$sql =~ s/\s*RETURN /return /;
	$sql =~ s/\|\|/+/gs;
	$sql = var_upcase($sql);
	$MR->log_msg("convert_return: $sql");
	# if ($PRESCAN{SETOF})
	# {
	# 	$sql = "return $CFG{setoff_table_param};";
	# 	$PRESCAN{SETOF_RETURN_EXECUTED} = 1;
	# }

	if($LAST_EXCEPTION_NAME ne '')
	{
		$EXCEPTIONS->{$LAST_EXCEPTION_NAME}->{then}.=$sql;
		return '';
	}

	$sql =~ s/^\s*return\s*//gis;
	$sql = $MR->trim($sql);
	if($LAN->is_complex_expression($sql))
	{
		$sql = JS_substitute({
			VAR => 'RETURN_VALUE',
			SQL => $sql,
			TEMPLATE => 'var_assignment_wrapper'
			});
		
		$sql =~ s/(\{sqlText\:\s+\`)(\w+\.\w+)\(\`/$1CALL $2(`/gis;
		$sql =~ s/(\{sqlText\:\s+\`)(\w+)\(\`/$1CALL $2(`/gis;
		
		return code_indent($sql . "return RETURN_VALUE");
	}

	$sql = code_indent('return ' . $CONVERTER->convert_sql_fragment($MR->trim($sql),{STATEMENT_CATEGORY=>"JAVASCRIPT"}));
	return $sql . ' ' . $comment;
}

sub raise_notice
{
	my $ar = shift;
	my $sql = join("\n", @$ar);
	$sql =~ s/\n/ /gs;
	$sql =~ s/RAISE\s+(NOTICE|EXCEPTION)\s+//gis;
	$sql =~ s/\s*\;\s*//gis;
	$sql = $MR->trim($sql);
	$sql = '\'Notice : ' . $sql ;
	$sql =~ s{('.*?)'(.*)}{$1$2};
	$sql = var_upcase($sql);
	$sql = 'console.log(' . $sql . ');';
	return code_indent($sql);
}

sub raise_notice_old
{
	my $ar = shift;
	my $sql = join("\n", @$ar);
	$sql =~ s/\n/ /gs;
	my @tok = $LAN->split_expression_tokens($sql);
	#print "TOKENS: " . Dumper(\@tok);
	shift @tok; #get rid of RAISE
	shift @tok if ($tok[0] eq 'NOTICE'); #get rid of NOTICE
	my $msg = shift @tok;
	while ($msg =~ /\[\%\]/)
	{
		my $comma = shift @tok;
		my $param = shift @tok;
		$msg =~ s/\[\%\]/\{$param\}/;
	}
	#$sql =~ s/raise\s+notice/print(/gis;
	#$sql .= ')';
	$msg = adjust_expr($msg);
	$msg = "throw ($msg);";
	return code_indent($MR->trim($msg));
}

sub execute_into
{
	my $ar = shift;
	my $sql = join("\n", @$ar);
	#$sql =~ s/\n/ /gs;
	$MR->log_msg("execute_into: $sql");
	#$sql =~ s/\n/ /gs;
	if($sql =~ /EXECUTE\s+IMMEDIATE\s+(.*)INTO\s+(.*)/is)
	{
		my $dynamic_sql = $1;

		my $var_name = $2;
		$var_name =~ s/\;$//;
		$var_name =~ s/^\s+//g;
		$var_name = uc($var_name);
		$VARIABLES{$var_name} = 1;
		
		$dynamic_sql =~ s/\;$//;
		$dynamic_sql =~ s/^\s+//g;
		$dynamic_sql =~ s/^'//;
		$dynamic_sql =~ s/'\s*$//;

		$dynamic_sql = JS_substitute({
			SQL => $dynamic_sql,
			VAR => $var_name,
			TEMPLATE => 'var_assignment_wrapper'
		});
		
		if($LAST_EXCEPTION_NAME ne '')
		{
			$EXCEPTIONS->{$LAST_EXCEPTION_NAME}->{then}.=$dynamic_sql;
			return '';
		}
		return code_indent($dynamic_sql);
	}

	my @tok = $LAN->split_expression_tokens($sql);
	my ($exec_kw, $stmt, $into, $var) = @tok;
	$stmt = adjust_expr($stmt);
	return code_indent("$var = $CFG{dbh_varname}.select_value($stmt)");
	#return $sql;
}


sub adjust_expr
{
	my $expr = shift;
	my $quote = '"';
	my $multiline_flag = 0;
	if ($expr =~ /\n/)
	{
		$quote = '"""';
		$multiline_flag = 1;
	}
	$MR->log_msg("adjust_expr: multiline: $multiline_flag, SQL: $expr");
	#my $
	#$expr =~ s/\|\|/\ + /g; # || to +
	#$expr =~ s/\'\'\'/\\\'\\\'/g; #consecutive single quptes escape
	#handle escape quotes
	my $len = length($expr);
	my @chars = map {substr( $expr, $_, 1)} 0 .. $len -1;
	my $inside_str = 0;
	my$i = 0;
	while ($i < $len)
	{
		#handle quote escape
		my $orig_char = $chars[$i];
		#print "CHAR: $orig_char, inside: $inside_str\n";
		if ($orig_char eq "'" && !$inside_str)
		{
			$inside_str = 1;
			$chars[$i] = $quote;
		}
		elsif ($orig_char eq "'" && substr($expr,$i,2) eq "''" && $inside_str)
		{
			#$inside_str = !$inside_str;
			if ($inside_str)
			{
				#$chars[$i] = "\\'";
				#$chars[$i+1] = "\\'";
				$chars[$i+1] = ""; #no need for the escape single quote
				$i+2;
			}
		}
		elsif ($orig_char eq "'" && $inside_str)
		{
			$inside_str = 0;
			$chars[$i] = $quote;
		}

		#handle concat
		if ($chars[$i] eq "|" && substr($expr,$i,2) eq "||" && !$inside_str)
		{
				$chars[$i] = " + ";
				$chars[$i+1] = "";
				$i+2;
		}

		$i++;
	}
	$expr = join("", @chars);
	$expr =~ s/\;$//; #get rid of closing semicolon
	$expr = $MR->trim($expr);
	return $expr;
}

sub convert_else_if
{
	my $ar = shift;
	return '' if $STOP_OUTPUT;
	my $sql = join("\n", @$ar);
	$sql =~ s/^\s+|\s+$//g;
	if(substr $sql, -1 eq ';')
	{
		chop $sql;
	}
	
	$MR->log_msg("Starting convert_else_if: $sql");
	if ($sql =~ /^\s*ELSE.*IF\s+(.*?)\s+THEN\s*(.*)\s*/is || $sql =~ /^\s*ELSIF(.*)THEN(.*)/is)
	{
		my $cond = $1;
		my $end = $2;
		$INDENT--;
		if($cond =~ /^\(.*?\)$/)
		{
			$cond =~ s/^\((.*?)\)$/$1/;
		}

		my $tmp = $MR->trim($cond);
		my $conv = $MR->trim($CONVERTER->convert_sql_fragment($tmp, {STATEMENT_CATEGORY=>"JAVASCRIPT"}));
		if ($conv ne $tmp)
		{
			$cond = $conv;
		}
		
		my $ret = code_indent("\n}\nelse if($cond)\n{");

		$INDENT++;
		if ($end ne '')
		{
			$ret .= "\n" . code_indent($end);
		}
		$DB::single = 1;

		return $ret;
	}
}

sub convert_else
{
	my $ar = shift;
	my $sql = join("\n", @$ar);
	$MR->log_msg("Starting convert_else: $sql");
	if ($sql =~ /^\s*ELSE(.*)/i)
	{
		$INDENT--;
		my $ret = code_indent("\n}\nelse\n{");
		$INDENT++;
		return $ret;
	}
}

sub convert_end_if
{
	return '' if($STOP_OUTPUT || $IF_COUNT<1);
	$IF_COUNT--;
	$INDENT--;
	return code_indent("}");
}

sub convert_start_if
{
	my $ar = shift;
	return '' if $STOP_OUTPUT;
	my $sql = join("\n", @$ar);
	$MR->log_msg("convert_start_if: $sql");
	if ($sql =~ /^\s*IF\s*(.*?)\s+THEN\s*(.*)\s*/is)
	{
		$IF_COUNT++;
		my ($cond,$rest) = ($1, $2);
		$MR->log_msg("convert_start_if 1 SQL: $sql, COND $cond, REST: $rest");
		
		$cond =~ s/\=/\=\=/g;
		$cond =~ s/\n/ /g;

		if($cond =~ /^\(.*?\)$/)
		{
			$cond =~ s/^\((.*?)\)$/$1/;
		}

		my $NVL_STATEMENT = '';
		if($cond =~ /\bNVL\s*\((.*?),(.*?)\)/is)
		{
			$NVL_STATEMENT = code_indent("if(!$1)") . "\n" . code_indent("{") . "\n";
			$INDENT++;
			$NVL_STATEMENT .= code_indent("var NVL_VALUE = $2;") . "\n";
			$INDENT--;
			$NVL_STATEMENT .= code_indent("}\nelse\n{") . "\n";
			$INDENT++;
			$NVL_STATEMENT .= code_indent("var NVL_VALUE = $1;") . "\n";
			$INDENT--;
			$NVL_STATEMENT .= code_indent("}") . "\n";

			$cond =~ s/\bNVL\s*\((.*?),(.*?)\)/NVL_VALUE/;
		}
		
		$cond = var_upcase($cond);
		#my $tmp = "CONDITIONAL:" . $MR->trim($cond);
		$MR->log_msg("Conditional conversion: $cond");
		$cond = $MR->trim($CONVERTER->convert_sql_fragment($cond, {STATEMENT_CATEGORY=>"JAVASCRIPT"}));
		#$conv =~ s/^CONDITIONAL://;
		my $ret = '';
		#if ($conv ne $tmp)
		#{
		#	$cond = $conv;
		#}

		#$cond =~ s/[^<]\=[^>]/\=\=/g;
		$ret = code_indent("if ($cond)\n{");
		$INDENT++;
		
		if ($rest =~ /(.*)END IF/i)
		{
			$IF_COUNT--;
			$ret .= " " . $MR->trim($CONVERTER->convert_sql_fragment($1)) . " " . convert_end_if();
			$MR->log_msg("convert_start_if: DEBUG 05, REST: $rest");
		}
		elsif ($rest)
		{
			$MR->log_msg("convert_start_if: DEBUG 10, REST: $rest");
			$rest = $CONVERTER->convert_sql_fragment($rest);
			$rest = convert_subCode([$rest]);
			$ret .= "\n" . code_indent($MR->trim($rest)) . " ";
		}
		return $NVL_STATEMENT . $ret;
	}
	#elsif ($sql =~ /^\s*IF(.*)\s(.+)/is) #attempt to parse.  primitive for now
	elsif ($sql =~ /^\s*IF(.*)/is)
	{
		$IF_COUNT++;
		#my ($cond,$rest) = ($1, $2);
		my $cond = $1;
		#$MR->log_msg("convert_start_if 2 SQL: $sql, COND $cond, REST: $rest");
		$MR->log_msg("convert_start_if 2 SQL: $sql, COND $cond");
		$cond =~ s/\=/\=\=/g;
		$cond =~ s/\n/ /g;

		my $NVL_STATEMENT = '';
		if($cond =~ /\bNVL\s*\((.*?),(.*?)\)/)
		{
			$NVL_STATEMENT = code_indent("if(!$1)") . "\n" . code_indent("{") . "\n";
			$INDENT++;
			$NVL_STATEMENT .= code_indent("var NVL_VALUE = $2;") . "\n";
			$INDENT--;
			$NVL_STATEMENT .= code_indent("}\nelse\n{") . "\n";
			$INDENT++;
			$NVL_STATEMENT .= code_indent("var NVL_VALUE = $1;") . "\n";
			$INDENT--;
			$NVL_STATEMENT .= code_indent("}") . "\n";

			$cond =~ s/\bNVL\s*\((.*?),(.*?)\)/NVL_VALUE/;
		}


		$cond = var_upcase($cond);
		$cond = $MR->trim($CONVERTER->convert_sql_fragment($cond));
		#$rest =~ s/RETURN/return/i;
		#if (! ($rest =~ /^RETURN/i) )
		#{
		#	$rest = $MR->trim($CONVERTER->convert_sql_fragment($rest));
		#}
		#my $ret = "if ($cond)\n{$rest}";
		my $ret = "if ($cond)";
		return code_indent($ret);
	}
	else
	{
		$MR->log_msg("convert_start_if handler called, but can't match the pattern: $sql");
		return code_indent($sql);
	}
}

sub plug_indent_OLD
{
	my $str = shift;
	my $indent = "\t" x $INDENT ;
	$str =~ s/\n/\n$indent/gs;
	$str = $indent . $str;
	return $str;
}

sub convert_conditions
{
	my $str = shift;
	return $str unless $str =~ /\=/; #check for equal signs
	my @tok = $LAN->split_expression_tokens($str);

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
		$open_brace = "$CFG{code_indent}\n";
	}
	elsif ($sql =~ /\braise\s+exception\s+(.*)/gis)
	{
		$exception_name = $1;
		$open_brace = "$CFG{code_indent}\n";
	}
	$exception_name =~ s/--/\/\//gis;
	my $exc = "$open_brace$CFG{code_indent}$CFG{code_indent}throw $exception_name;";
	$exc =~ s/\;\s*\;/;/g;
	return $exc;
	#$sql =~ s/EXCEPTION\s+WHEN\s+OTHERS\s+THEN//gis;
	#$sql = raise_notice([$sql]);

	#$INDENT_ENTIRE_SCRIPT = 1;
	#return "$EXCEPTION_BLOCK:$sql";	
}

sub suppress_EXCEPTION_WHEN_OTHERS
{
	return "/* Suppressed EXCEPTION_WHEN_OTHERS.  Handled in catch-all */";
}

sub handle_exceptions
{
	my $ar = shift;
	my $sql = join("\n", @$ar);
	$MR->log_msg("handle_exceptions: $sql");
	$sql =~ s/EXCEPTION\s+WHEN\s+OTHERS\s+THEN//gis;
	$sql = raise_notice([$sql]);

	$INDENT_ENTIRE_SCRIPT = 1;
	return "$EXCEPTION_BLOCK:$sql";
}

sub handle_program_conclusion
{
	my $ar = shift;
	my $sql = join("\n", @$ar);
	return "//PROGRAM ENDED\n";
}

sub finalize_content
{
	my $ar = shift;
	my $options = shift;
	my $indent_start = $options->{db_connect_init_call_index};
	$MR->log_msg("finalize_content: indent_start: $indent_start");
	my $do_indent = 1;

	foreach (@$ar)
	{
		if($PROCEDURE_NAME ne 'UNKNOWN_PROC')
		{
			$_ =~ s/\%PROCEDURE_NAME%/$PROCEDURE_NAME/g;
			$_ =~ s/%CONVERT_TYPE%/Procedure/g;
			$_ =~ s/%STANDARD_VAR%/$CFG{standard_proc_var}/g;
		}
		elsif($FUNCTION_NAME ne 'UNKNOWN_FUNCTION')
		{
			$_ =~ s/\%FUNCTION_NAME%/$FUNCTION_NAME/g;
			$_ =~ s/%CONVERT_TYPE%/Function/g;
			$_ =~ s/%STANDARD_VAR%/$CFG{standard_func_var}/g;
		}
		$_ =~ s/\%UNDEFINED_WHILE_LOOP_(\d+)%/$UNDEFINED_WHILE_LOOPS->{COMPLETE}->{$1}/g;
	}

	if ($INDENT_ENTIRE_SCRIPT)
	{
		my $curr_idx = 0;
		foreach (@$ar)
		{
			if ($_ =~ /^$EXCEPTION_BLOCK/)
			{
				$_ =~ s/$EXCEPTION_BLOCK\://;
				$_ =~ s/\n/\n\t/gs;
				$_ = "\t$_";
				$_ = "except snowflake.connector.errors.ProgrammingError as e:\n" . $_;
				$do_indent = 0;
			}
			elsif ($do_indent)
			{
				if ($indent_start >= 0 && $curr_idx == $indent_start)
				{
					$_ = "try:\n$_";
				}
				if ($indent_start >= 0 && $curr_idx >= $indent_start)
				{
					$_ =~ s/\n/\n\t/g;
					$_ = "\t" . $_ if $curr_idx > $indent_start;
				}
			}
			$curr_idx++;
		}
	}
}

sub JS_substitute
{
	my $p = shift;
	my $templ = $CFG{$p->{TEMPLATE}};
	if (!$templ)
	{
		my $err =  "ERROR: NO TEMPLATE WAS PROVIDED OR FOUND $p->{TEMPLATE} " . Dumper($p);
		$MR->log_error($err);
		print STDERR "$err\n";
		return $err;
	}
	$STMT_CNT++;
	$p->{STMT_CNT} = $STMT_CNT;
	#print "AGRS FOR JS_CONTENT: " . Dumper($PRESCAN{ARG});

	my %regex_subst = (
		'\(' => '__OPEN_PAREN__',
		'\)' => '__CLOSE_PAREN__',
	);

	#substitute proc arguments
	if ($p->{SQL})
	{
		$MR->log_msg("FRAGMENT BEFORE: $p->{SQL}");
		$p->{SQL} = $MR->trim($CONVERTER->convert_sql_fragment($p->{SQL}));
		$MR->log_msg("FRAGMENT AFTER: ********\n$p->{SQL}\n********");
	}

	if ($MR->trim($p->{SQL}) eq '')
	{
		$STMT_CNT--;
		return '' unless $p->{NO_SQL_PROCEED};
	}

	#$MR->log_msg("JS CHECK 0");
	$MR->log_msg("JS CHECK 0. USE_VARIABLE_QUOTE: " . Dumper(\%USE_VARIABLE_QUOTE));
	#$USE_VARIABLE_QUOTE
	if ($PRESCAN{ARG} && $p->{SQL})
	{
		foreach my $k (values %{$PRESCAN{ARG}})
		{
			$k = uc($k);
			my $val = $k; #make a copy
			$val =~ s/\[\]//gis; #get rid of []
			my $q = ($USE_VARIABLE_QUOTE{$k} or $USE_VARIABLE_QUOTE{$val})?"'":"";
			$MR->log_msg("JS ITER ON ARG '$val'");
			$p->{SQL} =~ s/\'\|\|$val\|\|\'/$val/gis;
			$p->{SQL} =~ s/\b$val\b/$q` + $val + `$q/gis;
		}
	}
	$MR->log_msg("JS CHECK 1");

	my %var_seen = (); #for upper/orig cases
	if (%VARIABLES && $p->{SQL})
	{
		foreach my $k (sort {length($b) <=> length($a) } keys %VARIABLES)
		{
			next if $MR->trim($k) eq '';
			$k = uc($k);
			my $seen_flag = $var_seen{$k} || 0;
			$MR->log_msg("JS CHECK 1.5, VAR $k, seen_flag: $seen_flag.  Skipping if seen");
			next if $seen_flag;
			$var_seen{$k} = 1;
			if ($p->{SQL} =~ /^`($k)`$/i)
			{
				$p->{SQL} = uc($k);
				$MR->log_msg("Getting rid of ticks in SQL, because there is nothing else in it. Var $k, SQL: $p->{SQL}");	
			}
			if ($p->{SQL} =~ /^$k$/i || $p->{SQL} =~ /^`$k`$/i)
			{
				$p->{SQL} = uc($k);
				$templ =~ s/`//gs; #get rid of the ticks in the template
				$MR->log_msg("Skipping var substitution in SQL, because there is nothing else in it. Var $k, SQL: $p->{SQL}");
				next;
			}
			my $q = $USE_VARIABLE_QUOTE{$k}?"'":"";
			my $v = $k;
			$MR->log_msg("JS CHECK 2.5, VAR $k, QUOTE: $q, V: $v");
			my ($before, $after) = ('','');
			if ($VAR_BEFORE_AFTER_CALL{$k})
			{
				$before = $VAR_BEFORE_AFTER_CALL{$k}->{before};
				$after = $VAR_BEFORE_AFTER_CALL{$k}->{after};
			}
			#we have cases where a variable is surrounded by quotes - may be a part of a display message or a string in the WHERE clause.  change it, and then change it back
			my $TEMP_QUOTE = '__TEMPQUOTE__';
			$p->{SQL} =~ s/'($k)'/$TEMP_QUOTE$1$TEMP_QUOTE/gis;

			#$v = $LAST_ROWCOUNT_VAR if($VARIABLES{$k} eq $LAST_ROWCOUNT_VAR); #special case
			$p->{SQL} =~ s/\'\s*\|\|\s*$k\s*\|\|\s*\'/ $v /gis;
			$p->{SQL} =~ s/\'\s*\|\|\s*$k\s*\|\|/$v /gis;
			$p->{SQL} =~ s/\'\s*\|\|\s*$k\s*$/ $v/gis;
			$p->{SQL} =~ s/\b$k\b/$before$q` + $v + `$q$after/gis;
			$p->{SQL} =~ s/$TEMP_QUOTE/'/gis; #change it back
			# a variable may be an array, and its index is accessed within a loop.  Adjust the position of [i] convention
			$p->{SQL} =~ s/$v \+ `'(\[\w+\])/$v$1 + `'/gis; #changes IN_IMPORT_RUN_ID + `'[i]`to IN_IMPORT_RUN_ID[i] + `'
		}
	}
	$MR->log_msg("JS CHECK 2");

	foreach my $k (keys %$p)
	{
		$templ =~ s/\%$k\%/$p->{$k}/gs;
	}
	$MR->log_msg("JS CHECK 3:\n$templ");
	if ($CFG_POINTER->{js_wrapper_subst})
	{
		$MR->log_msg("Section js_wrapper_subst found in config.");
		foreach my $el (@{$CFG_POINTER->{js_wrapper_subst}})
		{
			my ($mp, $from, $to) = ($el->{matching_pattern}, $el->{from}, $el->{to});
			next unless $templ =~ /$mp/gis;
			$templ =~ s/$from/$to/gis;
		}
	}
	return $templ;
}

sub assign_var_before_after_call
{
	my ($varname, $type) = @_;
	$MR->log_msg("assign_var_before_after_call called with $varname, type: $type.  ptr: " . Dumper($CFG_POINTER->{eclose_in_sql_call}));
	return unless $CFG_POINTER->{eclose_in_sql_call};
	foreach my $k (keys %{$CFG_POINTER->{eclose_in_sql_call}})
	{
		next unless $type =~ /$k/gis;
		my $el = $CFG_POINTER->{eclose_in_sql_call}->{$k};
		$MR->log_msg("eclose_in_sql_call found for var $varname: " . Dumper($el));
		$VAR_BEFORE_AFTER_CALL{$varname} = $MR->deep_copy($el);
		$VAR_BEFORE_AFTER_CALL{uc($varname)} = $MR->deep_copy($el);
	}
}


sub JS_substitute_OLD
{
	my $p = shift;
	my $templ = $CFG{$p->{TEMPLATE}};
	if (!$templ)
	{
		my $err =  "ERROR: NO TEMPLATE WAS PROVIDED OR FOUND $p->{TEMPLATE} " . Dumper($p);
		print STDERR "$err\n";
		return $err;
	}
	$STMT_CNT++;
	$p->{STMT_CNT} = $STMT_CNT;
	#print "AGRS FOR JS_CONTENT: " . Dumper($PRESCAN{ARG});

	my %regex_subst = (
		'\(' => '__OPEN_PAREN__',
		'\)' => '__CLOSE_PAREN__',
	);

	#substitute proc arguments
	if ($p->{SQL})
	{
		$MR->log_msg("FRAGMENT BEFORE: $p->{SQL}");
		$p->{SQL} = $MR->trim($CONVERTER->convert_sql_fragment($p->{SQL}));
		$MR->log_msg("FRAGMENT AFTER: ********\n$p->{SQL}\n********");
	}

	if ($MR->trim($p->{SQL}) eq '')
	{
		$STMT_CNT--;
		return '';
	}

	#foreach my $k (keys %regex_subst)
	#{
	#	my $v = $regex_subst{$k};
		#$p->{SQL} =~ s/$k/$v/gis;
	#}
	$MR->log_msg("JS CHECK 0");
	my %proc_args = ();
	if ($PRESCAN{ARG} && $p->{SQL})
	{
		foreach my $k (values %{$PRESCAN{ARG}})
		{
			$proc_args{$k} = 1;
			my $q = ($USE_VARIABLE_QUOTE{$k} or $USE_VARIABLE_QUOTE{uc($k)})?"'":"";
			$k = uc($k);
			$MR->log_msg("JS ITER ON ARG '$k'");
			$p->{SQL} =~ s/\'\|\|$k\|\|\'/$k/gis;
			$p->{SQL} =~ s/\b$k\b/$q` + $k + `$q/gis;
		}
	}
	$MR->log_msg("JS CHECK 1");

	my %var_seen = (); #for upper/orig cases
	if (%VARIABLES && $p->{SQL})
	{
		foreach my $k (sort {length($b) <=> length($a) } keys %VARIABLES)
		{
			$k = uc($k);
			next if $proc_args{$k};
			my $seen_flag = $var_seen{$k} || 0;
			$MR->log_msg("JS CHECK 1.5, VAR $k, seen_flag: $seen_flag.  Skipping if seen");
			next if $seen_flag;
			$var_seen{$k} = 1;
			if ($p->{SQL} =~ /^`($k)`$/i)
			{
				$p->{SQL} = uc($k);
				$MR->log_msg("Getting rid of ticks in SQL, because there is nothing else in it. Var $k, SQL: $p->{SQL}");	
			}
			if ($p->{SQL} =~ /^$k$/i || $p->{SQL} =~ /^`$k`$/i)
			{
				$p->{SQL} = uc($k);
				$templ =~ s/`//gs; #get rid of the ticks in the template
				$MR->log_msg("Skipping var substitution in SQL, because there is nothing else in it. Var $k, SQL: $p->{SQL}");
				next;
			}
			my $q = $USE_VARIABLE_QUOTE{$k}?"'":"";
			my $v = $k;
			$MR->log_msg("JS LOOP: V: $v, K: $k, Q: $q");
			#$v = $LAST_ROWCOUNT_VAR if($VARIABLES{$k} eq $LAST_ROWCOUNT_VAR); #special case
			#$p->{SQL} =~ s/\'\s*\|\|\s*$k\s*\|\|\s*\'/ $v /gis;
			#$p->{SQL} =~ s/\'\s*\|\|\s*$k\s*\|\|/$v /gis;
			#$p->{SQL} =~ s/\'\s*\|\|\s*$k\s*$/ $v/gis;
			$p->{SQL} =~ s/\b$k\b/$q` + $v + `$q/gis;
		}
	}
	$MR->log_msg("JS CHECK 2");

	foreach my $k (keys %$p)
	{
		$templ =~ s/\%$k\%/$p->{$k}/gs;
	}
	$MR->log_msg("JS CHECK 3");
	return $templ;
}


sub handle_for_loop_start
{
	my $ar = shift;
	my $sql = $MR->trim(join("\n", @$ar));
	$MR->log_msg("handle_for_loop_start: $sql");
	if ($sql =~ /FOR\s(.*)\s+IN\s+[(]*\s*(SELECT.*?)[)]*\s*LOOP/is)
	{
		$MR->log_msg("handle_for_loop_start: VARIANT 1");
		my ($var, $select) = ($1, $2);
		$var = uc($var);
		$VARIABLES{$var} = 1;
		my $js_sql = JS_substitute({
			VAR => $var,
			SQL => $select,
			TEMPLATE => 'dml_wrapper'
			});

		my $res_var_name = "res$STMT_CNT";
		$js_sql .= "while ($res_var_name.next()) {\n";
		$MR->log_msg("VAR: $var, SELECT: $select");
		$js_sql =~ s/$res_var_name/$var/gs;
		$sql = $js_sql;
	}
	if ($sql =~ /FOR\s(.*)\s+IN\s+[(]*\s*EXECUTE(.*?)[)]*\s*LOOP/is)
	{
		$MR->log_msg("handle_for_loop_start: VARIANT 1");
		my ($var, $select) = ($1, $2);
		$var = uc($var);
		$VARIABLES{$var} = 1;
		my $js_sql = JS_substitute({
			VAR => $var,
			SQL => $select,
			TEMPLATE => 'dml_wrapper'
			});

		my $res_var_name = "res$STMT_CNT";
		$js_sql .= "while ($res_var_name.next()) {\n";
		$MR->log_msg("VAR: $var, SELECT: $select");
		$js_sql =~ s/$res_var_name/$var/gs;
		$sql = $js_sql;
	}
	elsif ($sql =~ /FOR\s+(.*)\s+IN\s+(\d+)\.\.\((.+)\)\s*LOOP/is)
	{
		my ($var, $loop_start, $loop_end) = ($1,$2,$3);
		$var = uc($var);
		$VARIABLES{$var} = 1;
		$MR->log_msg("handle_for_loop_start: VARIANT 2, $var, $loop_start, $loop_end");
		$sql = "for($var=$loop_start; $var<=$loop_end; $var++) {";
	}
	elsif ($sql =~ /FOR\s+(.*)\s+IN\s+(\d+)\.\.LENGTH\((.+)\)\s*LOOP/is)
	{
		my ($var, $loop_start, $loop_end) = ($1,$2,$3);
		$var = uc($var);
		$VARIABLES{$var} = 1;
		$MR->log_msg("handle_for_loop_start: VARIANT 3, $var, $loop_start, $loop_end");
		$sql = "for($var=$loop_start; $var<=$loop_end".".length; $var++) {";
	}
	elsif ($sql =~ /WHILE(.*)LOOP(.*)/is)
	{
		#my ($var, $loop_start, $loop_end) = ($1,$2,$3
		my $inner = $1;
		my $rest = $MR->trim($2);
		$inner =~ s/\bor\b/\|\|/gis;
		$inner =~ s/\band\b/\&\&/gis;
		$inner =~ s/\bnot\b/\!/gis;
		$MR->log_msg("handle_for_loop_start: VARIANT 4");
		$inner = var_upcase($inner);
		$sql = "while($inner) {";
		if ($rest ne '')
		{
			#my $templ = ($rest =~ /\:\=/gis)?'var_assignment_wrapper':'dml_wrapper';
			if ($rest =~ /(\w*)\s*\:\=(.*)/gis)
			{
				my ($var,$sql) = ($1,$2);
				$rest = convert_assignment([$rest]);
			}
			else
			{
				$rest = convert_dml([$rest]);
			}
			$sql .= "\n" . $rest;
		}
	}
	elsif ($sql =~ /FOR\s(.*)\s+IN EXECUTE\s+\'(SELECT.*)\'\s*LOOP/is)
	{
		my ($var, $select) = ($1, $2);
		$select =~ s/\'\'/\'/gs;
		$MR->log_msg("handle_for_loop_start: VARIANT 5, VAR: $var, SELECT: $select");
		
		my $js_sql = JS_substitute({
			VAR => $var,
			SQL => $select,
			TEMPLATE => 'dml_wrapper'
			});
		my $res_var_name = "res$STMT_CNT";
		$js_sql .= "while ($res_var_name.next()) {\n";
		$MR->log_msg("VAR: $var, SELECT: $select");
		$js_sql =~ s/$res_var_name/$var/gs;
		$sql = "//$sql\n$js_sql";
		$CURSORS{$var} = 1;
	}
	elsif($sql =~ /FOR\s+(\w+)\s+IN\s+(\w+)\s+LOOP\s+(.*?);/is)
	{
		my $item_name = $1;
		my $table_name = $2;
		my $statement = $3;
		$item_name = uc($item_name);
		$VARIABLES{$item_name} = 1;
		
		$statement = JS_substitute({
			SQL => $statement,
			VAR => $item_name,
			TEMPLATE => 'dml_wrapper'
			});

		my $js_sql = code_indent("while ($table_name.next()){\n");
		$INDENT++;
		$js_sql .= code_indent($statement) . "\n";
		$INDENT--;
		$js_sql .= handle_loop_end($ar) if($sql =~ /END LOOP;/is);
		$js_sql =~ s/\s+END LOOP\s*//is;

		$sql = $js_sql;

		$MR->log_msg("handle_for_loop_start VARIANT 6");
		return $sql;
	}
	elsif($sql =~ /FOR\s+(\w+)\s+IN\s+(\w+)\s+LOOP\s*$/is)
	{
		$MR->log_msg("handle_for_loop_start VARIANT 7");
		my $item_name = $1;
		my $table_name = $2;
		$item_name = uc($item_name);
		$VARIABLES{$item_name} = 1;
		
		#THIS LINE SUB MAY NEED TO BE REMOVED AT END OF LOOP
		push(@{$CFG_POINTER->{line_subst}},
			{from => "\\b$item_name\\b", to => $table_name});

		$sql = code_indent("while ($table_name.next()){\n");
		$INDENT++;
		#$sql = $js_sql . code_indent("\n$item_name = $table_name.$item_name;");
		return $sql;
	}
	elsif($sql =~ /^\s*LOOP\s*$/is)
	{
		$MR->log_msg("handle_for_loop_start VARIANT 8");
		if(exists($UNDEFINED_WHILE_LOOPS->{COUNT}))
		{
			$UNDEFINED_WHILE_LOOPS->{COUNT}+=1;
		}
		else
		{
			$UNDEFINED_WHILE_LOOPS->{COUNT}=0;
		}
		my $count = $UNDEFINED_WHILE_LOOPS->{COUNT};
		$UNDEFINED_WHILE_LOOPS->{$count}->{STATEMENT}='while(';
		$UNDEFINED_WHILE_LOOPS->{$count}->{INDENT}=$INDENT;
		$UNDEFINED_WHILE_LOOP_SEEN = 1;

		$sql = "\%UNDEFINED_WHILE_LOOP_$count\%";
	}
	else
	{
		$sql .= ' // DO NOT KNOW HOW TO PARSE THIS LOOP!';
	}

	$sql = code_indent($sql);
	$INDENT++;
	return $sql;
}

sub handle_loop_end
{
	my $ar = shift;
	my $sql = join("\n", @$ar);
	$MR->log_msg("handle_loop_end: $sql");
	$INDENT--;
	return "" if $PRESCAN{SETOF}; #do not return anything, this is a setof function
	return code_indent('}');
	#return ''; # code_indent("} //LOOP END\n\n");
}

sub handle_undefined_while_loop_end
{
	my $ar = shift;
	my $sql = join("\n", @$ar);
	return '' if(!$UNDEFINED_WHILE_LOOP_SEEN || $STOP_OUTPUT);
	$MR->log_msg("handle_undefined_while_loop_end: $sql");
	if($sql =~ /EXIT\s+WHEN\s+(.*?);/is)
	{
		my $cond = $MR->trim($1);
		$MR->log_msg("handle_undefined_while_loop_end VARIANT 1 SQL: $sql, COND $cond");
		$cond = $CONVERTER->convert_sql_fragment($cond);

		my @keys = sort(keys($UNDEFINED_WHILE_LOOPS));
		my $latest_key = 'COUNT';
		while($latest_key eq 'COUNT' || $latest_key eq 'COMPLETE')
		{
			$latest_key = pop(@keys);
		}

		$cond = "while($cond)\n";
		my $temp = $INDENT;
		$INDENT = $UNDEFINED_WHILE_LOOPS->{$latest_key}->{INDENT};
		$cond .= code_indent("{");
		$INDENT = $temp;

		$UNDEFINED_WHILE_LOOPS->{COMPLETE}->{$latest_key}=$cond;
		delete $UNDEFINED_WHILE_LOOPS->{$latest_key};
	}

	return '';
}


sub handle_row_count
{
	my $ar = shift;
	my $sql = join("\n", @$ar);
	$MR->log_msg("handle_row_count: $sql");	
	my $res_var_name = "res$STMT_CNT";
	my $assignment_var = 'UNKNOWN_VARNAME';
	if ($sql =~ /GET DIAGNOSTICS\s+(\w+)\s*=\s*ROW_COUNT/is)
	{
		$assignment_var = uc($1);
	}
	elsif ($sql =~ /\s*(\w*)\s*\:\=\s*SQL\%ROWCOUNT/is)
	{
		$assignment_var = $1;
	}
	$assignment_var = uc($assignment_var);
	$LAST_ROWCOUNT_VAR = $MR->trim($assignment_var); #this is not used currently anywhere.
	$VARIABLES{'SQL%ROWCOUNT'} = $LAST_ROWCOUNT_VAR;
	$MR->log_msg("handle_row_count: variable name: $LAST_ROWCOUNT_VAR");
	return code_indent("res$STMT_CNT.next();\n$assignment_var = $res_var_name.getColumnValue(1);");
}

sub convert_interval
{
	my $ln = shift;
	$MR->log_msg("INTERVAL LINE: $ln\nEND OF INTERVAL LINE");
	return $ln;
}

sub handle_setof_for_loop
{
	my $ar = shift;
	my $sql = join("\n", @$ar);
	$MR->log_msg("handle_setof_for_loop 1: " . Dumper($ar));
	$MR->log_msg("handle_setof_for_loop 2:\$sql");
	my $select = '/* UNKNOWN SELECT */';
	if ($sql =~ /FOR.*EXECUTE(.*?)(SELECT.*)\bLOOP\s+(.*)RETURN/gis)
	{
		$select = $2;
		$MR->log_msg("handle_setof_for_loop VARIANT 1");
	}
	elsif ($sql =~ /FOR.*EXECUTE(.*?)(SELECT.*)/gis)
	{
		$select = $2;
		$MR->log_msg("handle_setof_for_loop VARIANT 2");
	}

	my $ctas = $CFG{create_table_for_setof} . "\n";
	my %subst = (
		TABLE_NAME => "` + $CFG{setoff_table_param} + `",
		SQL => $select
	);

	$MR->log_msg("SETOF SUBST: " . Dumper(\%subst));
	#$ctas =~ s/\%SQL\%/$select/gis; #do SQL first
	foreach my $k (sort keys %subst)
	{
		$ctas =~ s/\%$k\%/$subst{$k}/gis;
	}

	if ($CFG{setof_suppress_strings})
	{
		foreach my $k (@{$CFG{setof_suppress_strings}})
		{
			$ctas =~ s/$k//gis;
		}
	}

	return convert_dml([$ctas]);
}

sub suppress_pattern
{
	my $ar = shift;
	my $sql = join("\n", @$ar);
	$MR->log_msg("suppress_pattern:" . Dumper($ar));
	return "";
}

sub blank
{
	my $ar = shift;
	my $sql = join("\n", @$ar);
	$MR->log_msg("blank:" . Dumper($ar));
	return "";
}

sub unnamed_end
{
	my $ar = shift;
	return end_procedure_no_more_output($ar) if($procCount==1);
	$EXCEPTION_SEEN = 0;
	$LAST_EXCEPTION_NAME = '';
	$procCount--;
	return "";

}
sub final_end
{
	my $ar = shift;
	my $sql = join("\n", @$ar);
	$MR->log_msg("final_end:" . Dumper($ar));

	$EXCEPTION_SEEN = 0;
	$LAST_EXCEPTION_NAME = '';

	if ($PRESCAN{SETOF} && !$PRESCAN{SETOF_RETURN_EXECUTED})
	{
		return code_indent(convert_return($ar));
	}
	elsif ($PRESCAN{SETOF} && $PRESCAN{SETOF_RETURN_EXECUTED})
	{
		return '';
	}

	if($sql =~ /\s*END\s+(\w+)\s*;$/i)
	{
		my $proc_Name = $1;

		my @split = ();
		if($PROCEDURE_NAME ne 'UNKNOWN_PROC')
		{
			@split = split(/\./,$PROCEDURE_NAME)
		}
		elsif($FUNCTION_NAME ne 'UNKNOWN_FUNCTION')
		{
			@split = split(/\./,$FUNCTION_NAME)
		}

		if($proc_Name eq $split[-1] || $proc_Name eq $split[-1])
		{
			$procCount--;
			return end_procedure();
		}

	}
	elsif($procCount == 1)
	{
		$procCount--;
		return end_procedure();
	}
	$procCount--;
	$sql =~ s/\n/ /gis;
	#return "//FINAL END $sql";
	return "";
}


sub remove_begin_end
{
	my $sql = shift;
	$MR->log_msg("remove_begin_end $sql");

	$sql =~ s/\bbegin\b//gis;
	$sql =~ s/\bend;//gis;
	return $sql;

}

sub var_upcase
{
	my $sql = shift;
	$MR->log_msg("Upcasing $sql");
	print "VAR UPCASE VARS: " . Dumper(\%VARIABLES);
	if ($PRESCAN{ARG_NAME})
	{
		my $arg_cnt = 0;
		foreach my $pos (sort {$a <=> $b} keys %{$PRESCAN{ARG_NAME}})
		{
			my $v = $PRESCAN{ARG_NAME}->{$pos};
			$v = uc($v);
			$MR->log_msg("Upcasing var $v");
			$sql =~ s/\s$v\b/ $v/gis;
			$sql =~ s/^$v\b/$v/gis;
		}
	}

	my $arg_cnt = 0;
	foreach my $k (keys %VARIABLES)
	{
		#my $v = $PRESCAN{ARG_NAME}->{$pos};
		$k = uc($k);
		$MR->log_msg("Upcasing var $k");
		$sql =~ s/\s$k\b/ $k/gis;
		$sql =~ s/^$k\b/$k/gis;
	}

	return $sql;
}

sub handle_js
{
	my $ar = shift;
	my $js = join("\n", @$ar);
	return $CONVERTER->convert_sql_fragment($js);
}

sub convert_subCode
{
	my $ar = shift;
	my $sql = join("\n",@$ar);

	my $cat = '';
	$cat = $CONVERTER->categorize_statement($sql);
	$cat = '__DEFAULT_HANDLER__' if($cat eq '');
	$MR->log_msg("convert_subCode: SQL category: $cat");

	my $handler = $CFG{fragment_handling}->{$cat};
	$MR->log_msg("convert_subCode: fragment handling handler: $handler");
	my $eval_str = $handler . '([$sql]);';
	$sql = eval($eval_str);
	
	my $return = $@;
	if ($return)
	{
		$MR->log_error("************ EVAL ERROR: $return ************");
	}
	else
	{
		$MR->log_msg("convert_subCode: fragment converted: $sql");
	}
	return var_upcase($sql);
}

sub test
{
	my $str = "select 'test1 '' test2' || '''nother one'";
	print adjust_expr($str);
}

sub custom_split
{
	my($string)=@_;
	my $ln=0;
	my @members; 
	my $member='';	
	my $parenthes = 0;
	foreach my $cr (split('', $string))
	{
		$ln=$ln+1;
	
		if ($cr eq '(')
		{
			$parenthes=$parenthes+1;
		}
		if ($cr eq ')')
		{
			$parenthes=$parenthes-1;
		}
	
		if ($cr eq ',' and $parenthes==0)
		{
		push @members,$MR->trim($member);
			$member='';
		}
		elsif($ln == length($string))
		{
		$member=$member.$cr;
	
		push @members,$MR->trim($member);
		$member='';
		}
		else 
		{
			$member=$member.$cr;
		}
    }	
	
	return @members;
}

sub wrap_in_try_catch
{
	my $ar = shift;
	return '' if $STOP_OUTPUT;
	my $sql = join("\n", @$ar);
	$sql =~ s/\;$//;
	$sql =~ s/^\s+//g;

	my $new_sql = code_indent($MR->trim($CONVERTER->convert_sql_fragment($sql)));

	#find temp table
	if ($sql =~ /CREATE.*VOLATILE.*\sTABLE\s+(\w+)/gis)
	{
		my $tmp_table = $1;
		$MR->log_msg("Temporary table found in a statement: $tmp_table");
		push(@{$CFG_POINTER->{line_subst}},
			{from => $tmp_table, to => "\#$tmp_table", first_match => 1});
	}

	$MR->log_msg(  "START START START \n".$new_sql."\nEND EMD END");
	return "
BEGIN TRY
" . $new_sql . "
END TRY
BEGIN CATCH
            SET \@ERROR_MESSAGE = ERROR_MESSAGE();
            SET \@ERROR_NUMBER = ERROR_NUMBER();
            SET \@PROCESS_MESSAGE ='".$new_sql."'
            EXEC [COKE_EDM].[usp_InsertLog]\@process_message,\@error_message, \@error_number;
            THROW
END CATCH; 
"
}

sub prescan_code_bteq
{
	my $filename = shift;
	$FILENAME = $filename; #save in a global var
	print "******** prescan_code_bteq $filename *********\n";
	$PROCEDURE_NAME = $MR->get_basename($filename);
	$PROCEDURE_NAME =~ s/\..*$//; #get rid of file extension
	my $ret = {}; #hash to keep everything that needs to be captured
	%PRESCAN = ();
	
	my @cont = $MR->read_file_content_as_array($filename);

	$PRESCAN_MLOAD = 0;

	foreach my $ln (@cont)
	{
		my $tmp = $ln; #don't touch the original line
		while ($tmp =~ /\$(\w+)\b(?!\.)/p) #example $YEAR, $MONTH, but not $schema.table
		{
			my ($prematch, $match, $postmatch) = (${^PREMATCH}, ${^MATCH}, ${^POSTMATCH});
			$MR->log_msg("Env var found: $match");
			$match =~ s/\$/\@/;
			$PRESCAN{ARG_NAME}->{$match}++;
			$tmp = $prematch . '____' . $postmatch;
		}

		if ($ln =~ /^\s*\.BEGIN\s+IMPORT\s+MLOAD/)
		{
			$PRESCAN_MLOAD = 1;
		}
	}

	$MR->log_msg("prescan_code_bteq completed: " . Dumper(\%PRESCAN));
	if ($PRESCAN_MLOAD)
	{
		$MR->log_msg("MLOAD BEGIN COMMAND FOUND. INVOKING MLOAD PARSER");
	}

	my $ret = {PRESCAN_INFO => \%PRESCAN};
	return $ret;
	
}


sub handle_qualify
{
	my $sql = shift;
	$MR->log_msg("handle_qualify: processing SQL:\n$sql");

	my $iter = 0;

	while($sql =~ /\bQUALIFY\b/gisp)
	{
		my ($prematch, $match, $postmatch) = (${^PREMATCH}, ${^MATCH}, ${^POSTMATCH});
		$iter++;
		my $select_pos = rindex(uc($prematch), "SELECT");
		$MR->log_msg("SELECT pos: $select_pos: " . substr($prematch,$select_pos,10) . '...'); #debug message
		my $end_of_clause_pos = get_end_of_clause($postmatch);
		my $qualify_clause = substr($postmatch, 0, $end_of_clause_pos);
		$MR->log_msg("END OF CLAUSE POS: $end_of_clause_pos. Qualify clause: $qualify_clause");
		$sql =	substr($prematch, 0, $select_pos) . #before SELECT
				"SELECT * FROM (" . #adding outer select
				substr($prematch, $select_pos) . #rest of prematch including SELECT
				") CONV_ALIAS WHERE $qualify_clause" .
				substr($postmatch, $end_of_clause_pos); #rest of statement
		#last;
		if ($iter >= 100)
		{
			$MR->log_error("handle_qualify exceeded allowed iterations! $iter");
			last;
		}
	}

	return $sql;
}

#look for end of string or unbalanced closing parenthesis
sub get_end_of_clause
{
	my $str = shift; #eg: rank()over(partition by 1 order by EndDateTime desc)=1) x where flag = 'I'
	my $len = length($str);
	my $paren_cnt = 0;
	my $idx = 0;
	for(my $i = 0; $i < $len; $i++)
	{
		my $c = substr($str,$i,1);
		$paren_cnt++ if $c eq '(';
		$paren_cnt-- if $c eq ')';
		return $idx if $paren_cnt < 0; #unbalanced closing paren - end of clause
		$idx++;
	}

	return $idx
}

