use strict;
use Globals;
use Data::Dumper;
use Common::MiscRoutines;
use DWSLanguage;

my $MR = new Common::MiscRoutines;
my $LAN = new DWSLanguage();
my %CFG = (); #entries to be initialized
my $CFG_POINTER = undef;
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
my $DELIM = undef;
my $CATALOG;
my $VARIABLE_PREFIX = 'v_';
my %TABLE_VARS = (); #hash of table variables.  We do not want to substitute those variables with '{varname}'
my %TEMP_TABLES= ();
my $QUERY_INCREMENT = 0;
#my $TOKEN_DELIM = chr(31); # we will use it as a temporary 1-character replacement
my $WITH_PREFIX = "WITH____";
my $CASE_WHEN = {};
my @FRAGMENT_COMMENTS_SORTED = ();

my %REPLACE_TABLES = ();
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
my @PROCEDURE_PARAMS = ();
my @INTERNAL_PARAMS = ();
my $TABLES = {};
#my $table_params = {};

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
	#pop(@lines) if $lines[-1] =~ //
	$ret =~ s/\;\s*$//gis; #get rid of trailing semicolon
	$ret =~ s/\s*$//gis;
	$MR->log_msg("code_indent:: ''''$ret''''");
	return $ret;
}


sub get_all_tables
{
	my $cont = shift;
	my $final_tables = {};
	my @tables = ();
	my @insert_tables = $cont =~ /\bINSERT\b\s+\bINTO\b\s+(.*?)\s+/gis;
	my @from_tables = $cont =~ /\bFROM\b\s+(.*?)\s+/gis;
	my @join_tables = $cont =~ /\bJOIN\b\s+(.*?)\s+/gis;
	@tables = (@insert_tables,@from_tables,@join_tables);
	#$TABLES = {};
	foreach my $tbl (@tables)
	{
		$tbl =~ s/^\s+|\s+$//g;
		if(index($tbl,'@') == 0 or index($tbl,'(') == 0 or index($tbl,'.') == -1)
		{
			next;
		}
		$MR->log_msg("Processing table $tbl inside $PROCEDURE_NAME");
		$tbl = $MR->replace_single_pattern($MR->replace_single_pattern($tbl,'[',''),']','');
		$TABLES->{$tbl} = 1;
	}
	$MR->log_msg("All Tables: " . Dumper($TABLES));
}

# should be called by prescan_and_collect_info_hook in sql converter
sub prescan_code_synapse
{
	my $filename = shift;
	my $obj = shift;
	
	$CATALOG = $MR->read_json_config($obj->{object_catalog});
	$PROCEDURE_NAME = substr($filename,rindex($filename,'\\')+1,rindex($filename,'.') - rindex($filename,'\\')-1);
	$TABLES = {};
	get_all_tables($filename);
	print "******** prescan_code_synapse $filename *********\n";
	my $ret = {}; #hash to keep everything that needs to be captured

	#my $cont = $MR->read_file_content($filename);
	my @cont = $MR->read_file_content_as_array($filename);
	my $cont = join("\n", @cont);
	get_all_tables($cont);

	#$cont =~ s/@/v_/ig;
	my $proc_args = '';
	my $proc_vars = '';
	my @params =();
	@PROCEDURE_PARAMS = ();
	$cont =~ s/\-\-.*//gim;
	$cont =~ s/\/\*.*?\*\///gis;


	$cont =~ s/\bAS\b(.*?)\bBEGIN\b/\nAS\nBEGIN\n/gis;
	if ($cont =~ /CREATE\s+PROCEDURE\s+\[\w+\]\.\[\w+\](.*?)AS\s+BEGIN/gis ||
		$cont =~ /CREATE\s+PROC\s+\[\w+\]\.\[\w+\](.*?)AS\s+BEGIN/gis ||
		$cont =~ /CREATE\s+PROC\s+\[\w+\]\.\[\w+\](.*?)AS\b/gis)
	{
		$proc_args = $MR->trim($1);
		$MR->log_msg("Procedure args: $proc_args");
		@params = split(',',$1);
		foreach my $item (@params)
		{
			my @matched = $item=~/@(.*?)\s+/g;
			if(scalar(@matched)>0)
			{
				push(@PROCEDURE_PARAMS, $matched[0]);
			}
		}
	}
	else
	{
		$MR->log_msg("Cannot find proc args");
	}
	
	@params = $cont =~ /\bDECLARE\b\s+\@\w+\s+(?![\s*|T])/gi;
	$MR->log_msg("internal_params:\n");
	foreach my $item (@params)
	{
		my @matched = $item=~/@(.*?)\s+/g;
		if(scalar(@matched)>0)
		{
			push(@INTERNAL_PARAMS, "$VARIABLE_PREFIX$matched[0]");
		}
	}
	
	my @table_params = $cont =~ /\bDECLARE\b\s+@(.*?)\s+TABLE/gi;
	$MR->log_msg("table_params:\n");

	my @proc_args = map { $MR->trim($_) } split(/,/, $proc_args);
	my $pos = 0;
	############ 09/06 arg parsing needs to be improved
	foreach my $pa (@proc_args)
	{
		$pos++;
		$PRESCAN{ARG}->{$pos} = $pa;
		my @tmp = split(/ /, $pa);
		my $arg_name = shift(@tmp);
		my $arg_type = shift(@tmp);
		$PRESCAN{ARG_NAME}->{$pos} = uc($arg_name);
		$PRESCAN{ARG_TYPE}->{$pos} = $arg_type;
		my $arg_dir = shift(@tmp);
		if($arg_dir eq "OUTPUT" or $arg_dir eq "OUT")
		{
			$RETURN_TYPE = $arg_type;
		}
	}

	if(uc($cont) =~ /AS([\s\S]+)/)
	{
		my $body = $1;
		my $var_pos = 0;

		while($body =~ /DECLARE\s+(\w+)\s+([\w|\(|\)]+)/g)
		{
			$var_pos++;
			my ($varname, $vartype, $default) = ('','','');
			$varname = $1;
			$vartype = $2;
			print "FOUND VARIABLE " . $varname . "\n";
			if($cont =~ /SET\s+\Q$varname\E\s+=\s+(.*)\s+/)
			{
				$default = $1;
			}
			$PRESCAN{PROC_VARS}->{$var_pos} = {VARNAME => $varname, VARTYPE => $vartype, DEFAULT => $default};
		}
	}

	catalog_var_datatypes();
	$MR->log_msg("Prescan structure: " . Dumper(\%PRESCAN));
	$MR->log_msg("USE_VARIABLE_QUOTE1: " . Dumper(\%USE_VARIABLE_QUOTE));

	$ret->{PRESCAN_INFO} = undef;
	return $ret;
}



#useable
sub init_hooks #register this function in the config file
{
	my $param = shift;
	%CFG = %{$param->{CONFIG}};
	$CFG_POINTER = $param->{CONFIG}; #give the ability to modify config incrementally
	$Globals::ENV{CFG_POINTER} = \%CFG;
	$CONVERTER = $param->{CONVERTER};
	$MR = new Common::MiscRoutines unless $MR;
	print "INIT_HOOKS Called. MR: $MR. config:\n" . Dumper(\%CFG);


	#Reinitilize vars for when -d option is used:
	$INDENT = 0; #keep track of indents
	%PRESCAN = ();
	$STMT_CNT = 0;
	$PROCEDURE_NAME = 'UNKNOWN_PROC';
	$FUNCTION_NAME = 'UNKNOWN_FUNCTION';
	%VARIABLES = (); #catch variables along the way
	%USE_VARIABLE_QUOTE = ();
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
	%TABLE_VARS = ();
	%TEMP_TABLES = ();
	#$TABLES = {};
	$QUERY_INCREMENT = 0;
	#@PROCEDURE_PARAMS = ();
	%REPLACE_TABLES = ();
	$DELIM = $CFG_POINTER->{code_fragment_breakers}->{line_end}->[0];
	
	if ($CFG_POINTER->{catalog_file})
	{
        read_catalog_file();
    }
	
	$MR->log_msg("Statement delimiter: $DELIM");
	$MR->log_error("Statement delimiter not specified! Please supply it in code_fragment_breakers:line_end attribute.") unless $DELIM;
}

#useable
sub convert_comment
{
	my $ar = shift;
	my $comment = '"""' . "\n___COMMENT_START___" . join("\n", @$ar) . "\n___COMMENT_END___\n" . '"""';
	return code_indent($comment) . "\n";
}

sub remove_leftover_comment_closure
{
	my $ar = shift;
	my $sql = join("\n", @$ar);
	$MR->log_msg("remove_leftover_comment_closure:\n$sql");
	return ""; #give back an empty string
}

sub convert_table_var_declare
{
	my $ar = shift;
	my $sql = join("\n", @$ar);
	my @ret = split("\n", $sql);
	if ($sql =~ /DECLARE\s+\@(\w+)\s+TABLE\b/gis)
	{
		my $tbl_nm = $1;
		$MR->log_msg("Found declaration for table $tbl_nm");
		$TABLE_VARS{uc($tbl_nm)} = 1; #register it
		$sql =~ s/\s*\;\s*$//gis; #get rid of the trailing semicolon
		my $sql = $CONVERTER->convert_sql_fragment($MR->trim($sql));
		my @ret = split("\n", $sql);
	}
	push(@$ar,$CFG_POINTER->{create_table_suffix});
	return convert_dml(\@ret);
}

sub convert_var_declare
{
	my $ar = shift;
	my $sql = join("\n", @$ar);
	my @ret = split("\n", $sql);
	if ($sql =~ /\bDECLARE\s+\@(\w+)/gis)
	{
		my $var_nm = $1;

		my $val = "";
		$val = $1 if $sql =~ /\=\s*(.*)/gis;
		$val =~ s/\;//gis;
		if ($CFG_POINTER->{set_lowercase})
		{
			$var_nm =~ s/\b(\w+)\b/\L$var_nm/gi;
		}
		return "dbutils.widgets.text(\"$var_nm\", \"$val\")\n$var_nm = dbutils.widgets.get(\"$var_nm\")\n";
	}
	return $sql;
}

sub convert_dml
{
	my $ar = shift;
	#return '' if $STOP_OUTPUT;
	my $sql = join("\n", @$ar);
	$MR->log_msg("convert_dml:\n$sql");
	
	my $ret = $CONVERTER->convert_sql_fragment($MR->trim($sql));
	#$MR->log_msg("convert_dml:\n$ret");
	$ret =~ s/\s*\;\s*$//gis; #get rid of the trailing semicolon
	$ret = replace_params_as_spark($ret, undef, 'query_'.$QUERY_INCREMENT); #pass a label as the 2nd arg for debugging
	$ret = $MR->trim($ret);

	$ret =~ s/__BB_COMMENT_([0-9]+)__/__BB_COMMENT_SPARK_$1__/gis;

	$ret = 'spark.sql(' . $ret . ')';
	
	$QUERY_INCREMENT += 1;

	return code_indent($ret) . "\n";
}

sub replace_params_as_spark
{
	my $script = shift;
	my $is_assignment = shift;
	my $label = shift || 'unknown label';
	my @script_variables = $script =~ /(@.*?)[\s+|,|*(,)]/gis;
	my %seen;
	my @unique_script_variables = grep { !$seen{$_}++ } @script_variables;
	$MR->log_msg("replace_params_as_spark. Script vars ($label):\n" . join("\n", @unique_script_variables) . "\nTABLE_VARS: " . Dumper(\%TABLE_VARS));
	
	foreach my $pound_tbl (keys %TEMP_TABLES)
	{
		$script =~ s/\#$pound_tbl/$pound_tbl/gis;
	}

	my $format_text = '';
	if(scalar(@script_variables) > 0)
	{
		foreach my $item (@unique_script_variables)
		{
			$item = substr($item,1);
			if ($TABLE_VARS{uc($item)})
			{
				$MR->log_msg("Skipping substitution for table var $item");
				$script = $MR->replace_single_pattern($script,'@'.$item, $item);
			}
			else
			{
				$script = $MR->replace_single_pattern($script,'@'.$item, "'{".$VARIABLE_PREFIX.$item."}'");
				#$script =~ s/\@$item/'\{$item\}'/gis;
			}
			#$script =~ s/(\@$item)[\s+|,]/$item/gis;
		}
		$format_text = '.format(';
		foreach my $item (@unique_script_variables)
		{
			next if $TABLE_VARS{$item} or $TABLE_VARS{uc($item)}; #no need to include table variables
			$format_text .= "$item=$VARIABLE_PREFIX$item,";
		}
		chop $format_text;
		$format_text .= ')';
	
		if($is_assignment == 1)
		{
			$script = 'SELECT '. $script;
		}
		$script = 'f"""' . $script . '"""';#.$format_text;
	}
	else
	{
		if($is_assignment == 1)
		{
			$script = 'SELECT '. $script;
		}
		$script = 'f"""' . $script . '"""';
	}
	
	#do the final sweep and remove any @table_var references - replace with just variable
	foreach my $tbl (keys %TABLE_VARS)
	{
		$script =~ s/\@$tbl\b/$tbl/gis;
	}

	foreach my $procedure_param (@PROCEDURE_PARAMS)
	{
		$script =~ s/\@$procedure_param/'{$VARIABLE_PREFIX$procedure_param}'/gis;
	}
	return $script;
}

sub pre_finalization_handler_spark_sql
{
	my $fragments = shift;   # This is a ref to an array that we need to update in place

	foreach my $fragment (@{$fragments})
	{
		# Convert CREATE TABLE to a DataFrame
		if ($fragment =~ m{^\s*CREATE\s.*?\bTABLE\s+([#\w.]+)\s*(\(.*\))}si) 
		{  
		#	my $table_name = $1;
		#	my $create_rest = $2;
		#	if ($table_name =~ s{^\#}{})
		#	{
		#		$table_name = "$CFG_POINTER->{temp_table_prefix}$table_name";
		#	}
		#
		#	# Get the column defs (inside the (...) of the CREATE)
		#	if ($create_rest =~ m{
		#		(
		#			\(                      # Opening paren of "CREATE ("
		#			(?: [^()]* | (?0) )*    # content (bit in parens) of "CREATE (...)"
		#			\)   					# Closing paren
		#		)
		#						 }six)
		#	{
		#		my $col_defs = $1;
		#		$col_defs  =~ s{\(}{};  # Remove first "(", so that mask_commas gets any (...) for each col,
		#		                        # and NOT the whole (...) for the CREATE 
		#
		#		# Remove commas inside parens, so that we can split on comma to get each column def
		#		$col_defs =~ s{
		#		(
		#			\(                      # Opening paren (or whatever char you like)
		#			(?: [^()]* | (?0) )*    # Match a series of non-parens or another "self"
		#			\)                      # Closing char
		#		)
		#		}{mask_commas($1)}sexig;
		#
		#		# Get column names
		#		my @col_names = ();
		#		foreach my $col_def (split(/,/, $col_defs))
		#		{
		#			if ($col_def =~ m{(\w+)})
		#			{
		#				push(@col_names, "'$1'");   # Save col name surrounded by single quotes
		#			}
		#		}
		#
		#		# remove dots from table name
		#		$table_name =~ s/\./_/g;
		#
		#		# Create spark SQL code like this (example for table named tblx with cols col1 and col2): 
		#		#    columns = ['col1','col2']
		#		#    temp_tblx = spark.createDataFrame(schema=columns)
		#		#    temp_tblx.createOrReplaceTempView('temp_tblx')
		#		$fragment = "\ncolumns = [" . join(',', @col_names) . "]\n"
		#				  . "$table_name = spark.createDataFrame(schema=columns)\n"
		#				  . "$table_name.createOrReplaceTempView('$table_name')\n \n";
		#				  
		#	}

			$fragment =~ s/\s*\bidentity\s*\(.*?\)//gis;
			$fragment =~ s/\bnot\s+null//gis;
			$fragment =~ s/\bunique\b//gis;
			$fragment =~ s/\bnonclustered\s+\(.*?\)//gis;
			$fragment =~ s/\bwith\s+\(.*?\)//gis;
			$fragment =~ s/\s*\bon\s+primary//gis;
			# Convert any remaining "#" (temp) tables
			#$fragment =~ s{\b(INTO|FROM|TABLE)\s+\#}{$1 $CFG_POINTER->{temp_table_prefix}};
			$fragment = "spark.sql(\"\"\"$fragment\"\"\")";
		}

		#$fragment =~ s/\s*on\s+primary//gis;
		# Convert any remaining "#" (temp) tables
		$fragment =~ s{\b(INTO|FROM|TABLE)\s+\#}{$1 $CFG_POINTER->{temp_table_prefix}};
		#$fragment = "spark.sql(\"\"\"$fragment\"\"\")";
		$fragment = from_to_substitution($CFG_POINTER->{final_visual_subst}, $fragment) if $CFG_POINTER->{final_visual_subst};
	}

	# Now we have to check to see if we need to re-number the "query_<n>" 
	my $query_num = 0;
	my @truncated_table;
	my $used_header = 0;
	foreach my $fragment(@{$fragments})
	{
		$fragment =~ s{\bquery_([0-9]+)}{query_$query_num};
		$query_num++;

		#disable comments
		if (!$CFG_POINTER->{enable_comments})
		{
			$fragment =~ s/"""\s*___COMMENT_START___[\S\s]*___COMMENT_END___\s*"""//gis;
			$fragment =~ s/\/\*[\S\s]*\*\///gis;
			$fragment =~ s/--[\S\s]*//gis;
		}

		#if table name matches from previous truncate statement, switch to INSERT OVERWRITE statement
		if ($fragment =~ /"""INSERT\s+INTO\s+(.*)\s*?\n\s*\(/gis && exists $truncated_table[0] && $1 eq $truncated_table[0])
		{
			$fragment =~ s/"""INSERT\s+INTO\s+(.*)\s*?\n\s*\(/"""INSERT OVERWRITE INTO $1\n(/gis;
		}

		@truncated_table = $fragment =~ /[\S\s]*"""TRUNCATE\s+TABLE\s+(.*)"""[\S\s]*/gis;  #capture table name from TRUNCATE statement
		# $fragment =~ s/[\S\s]*"""TRUNCATE\s+TABLE\s+(.*)"""[\S\s]*//gis;  #remove TRUNCATE statement
		$fragment =~ s/[\S\s]*"""DELETE[\S\s]*//gis;  #remove DELETE statements

		#add INSERT or UPDATE conditional headers
		if (!$used_header && $fragment =~ /"""INSERT/gis)
		{
			$fragment = "\n" . $CFG_POINTER->{insert_header} . $fragment;
			$used_header = 1;
		}
		elsif (!$used_header && $fragment =~ /"""UPDATE/gis)
		{
			$fragment = "\n" . $CFG_POINTER->{update_header} . $fragment;
			$used_header = 1;
		}
	}
}

sub mask_commas 
# Return arg with all commas converted to "<:comma:>"
{
	my $text = shift;
	$text =~ s{,}{<:comma:>}g;
	return $text;
}

sub capture_comments
{
	my $cont = shift;
	my @part_comments = $cont =~ /(\/\*.*?\*\/|--.*?\n)/gs;
	return @part_comments;
}

sub capture_static_strings
{
	my $cont = shift;
	my @part_static_strings = $cont =~ /(\'.*?\')/gm;
	return @part_static_strings;
}

sub from_to_substitution
{
	my $array_string = shift;
	my $expression = shift;

	my @token_substitutions = @{$array_string};
	foreach my $token_sub (@token_substitutions)
	{
		my ($from, $to) = ($token_sub->{from}, $token_sub->{to});
		if ($expression =~ /$from/is)
		{
			while ($expression =~ s/$from/$to/is)
			{
				my @tokk = ($1,$2,$3,$4,$5,$6,$7,$8,$9);
				my $idxx = 1;
				foreach my $too (@tokk)
				{
					$expression =~ s/\$$idxx/$too/g;
					$idxx++;
				}
			}
		}
	}

	return $expression;
}

sub generic_substitution_string
{
	my $cont_str = shift;
	my $cfg_subst = shift;

	# my $cont_str = join("\n", @{$ar});

	$MR->log_msg("$cfg_subst Called. content: $cont_str");

	#block substitution for variable declarations from config
	if (exists $CFG_POINTER->{$cfg_subst})
	{
		$cont_str = from_to_substitution($CFG_POINTER->{$cfg_subst}, $cont_str);
	}

	return $cont_str;
}

sub post_conversion_adjustment_spark_sql
{
	my $everything = shift;

	# Get all variable names (e.g. v_...)
	my @vars = ();
	foreach my $line (@{$everything->{CONTENT}})
	{
		if ($line =~ m{\b$VARIABLE_PREFIX(\w+)})
		{
			push(@vars, $1);   # Save the name, sans prefix, e.g. v_abc gets saved as abc
		}
	}

	# Change variable names from '{...}' or @... syntax to v_... syntax
	foreach my $line (@{$everything->{CONTENT}})
	{
		foreach my $var (@vars)
		{
			$line =~ s{ '\{$var\}' }{{$VARIABLE_PREFIX$var}}xg;
			$line =~ s{  \@$var\b  }{$VARIABLE_PREFIX$var}xg;
		}
	}

	my $everything_string = join("\n", @{$everything->{CONTENT}});

	if ($CFG_POINTER->{keep_comments_in_place})
	{
		my $idx = 0;
		foreach my $comment (@FRAGMENT_COMMENTS_SORTED)
		{
			my $replacement = "__BB_COMMENT_" . $idx . "__";
			$everything_string =~ s/\Q$replacement\E/\"\"\"$comment\"\"\"/s;

			$replacement = "__BB_COMMENT_SPARK_" . $idx . "__";
			$everything_string =~ s/\Q$replacement\E/$comment/s;
			$idx++;
		}
	}

	if ($CFG_POINTER->{remove_duplicate_widget_definitions})
	{
		# Capture all widget definitions into an array, but capture the whole
		my @widget_defs = $everything_string =~ /dbutils.widgets.text\(\"(.*?)\", \".*?\"\)\n.*? = dbutils.widgets.get\(\".*?\"\)/gis;

		# Use a hash to track seen widgets and keep unique ones
		my %seen;
		my @unique_widget_defs;
		my @duplicate_widget_defs;

		foreach my $widget (@widget_defs)
		{
			if (!$seen{$widget}++)
			{
				push(@unique_widget_defs, $widget);
			}
			else
			{
				push(@duplicate_widget_defs, $widget);
			}
		}

		# Remove duplicate widget definitions, keeping only the first occurrence
		foreach my $widget (@duplicate_widget_defs)
		{
			$everything_string =~ s/dbutils\.widgets\.text\(\"$widget\"\, \".*?\"\)\n\bv_$widget = dbutils\.widgets\.get\(\"$widget\"\)//is;
		}
	}

	my $ar_inner = generic_substitution_string($everything_string, "final_subst");
	$ar_inner = generic_substitution_string($ar_inner, "final_after_subst");
	$everything->{CONTENT} = [split("\n", $ar_inner)];

	return $everything->{CONTENT};
}

sub convert_var_assignment
{
	my $ar = shift;
	my $sql = join("\n", @$ar);
	#$sql =~ s/\s*\;\s*$//gis;
	$sql =~ s/^\s*\;\s*$//gim;

	$MR->log_msg("convert_var_assignment:\n$sql");
	if ($sql =~ /SELECT\s+\@(\w+)\s*\=\s*(.*)/gis)
	{
		my ($var, $stmt) = ($1, $2); #assign tokens
		my $df_name = $var . "_df";
		if ($stmt =~ /^\(\s*SELECT\b(.*)\)$/) #get rid of SELECT inside 
		{
			$stmt = $MR->trim($1);
		}
		$MR->log_msg("convert_var_assignment:\nVAR: $var\nSQL: $stmt");

		my $is_assignment = 1;
		my $ret = $CONVERTER->convert_sql_fragment($MR->trim($sql));
		$stmt = $CONVERTER->convert_sql_fragment($MR->trim($stmt));
		$ret =~ s/\;\s*$//gis; #get rid of the trailing semicolon
		$ret =~ s/\@(\w+)/{$VARIABLE_PREFIX$1}/gis;
		#$ret = replace_params_as_spark($ret, $is_assignment, "assignment for $df_name");
		$ret =~ s/__BB_COMMENT_([0-9]+)__/__BB_COMMENT_SPARK_$1__/gis;

		$ret = "$VARIABLE_PREFIX$var = ".'spark.sql(f"""SELECT ' . $stmt . '""").first()[0]' . "\n";
		
		return code_indent($ret) . "\n";	
	}
	else
	{
		return "!!!!!!! Cannot match pattern in convert_var_assignment for $sql!";
	}
}

sub collect_case_when_in_hash
{
	my $content = shift;
	my $source_content = shift;
	my $iter = shift;
	if (!$iter)
	{
        $iter = 1;
    }

	while ($content =~ /(\bcase\s+when\b)(.*?\bend\b)/is)
	{
		my $cs_wh = $1;
		my $cs_wh2 = $2;
        
		if ($cs_wh2 =~ /\bcase\s+when\b/is)
		{
            $content = collect_case_when_in_hash($cs_wh2,$content,$iter);
			$source_content = $content;
			$iter += 1;
			next;
        }

        $CASE_WHEN->{'_CASE_WHEN_'.$iter} = $cs_wh.$cs_wh2;
		my $content_copy = $MR->deep_copy($CASE_WHEN->{'_CASE_WHEN_'.$iter});
		$content_copy = $MR->escape_regex_str($content_copy);
		$content =~ s/$content_copy/_CASE_WHEN_$iter/is;
		$source_content =~ s/$content_copy/_CASE_WHEN_$iter/is;
		$iter += 1;
    }
	while ($content =~ /(\bcase\s+\w+\.?\w*\s+when\b.*?\bend\b)/is)
	{
        $CASE_WHEN->{'_CASE_WHEN_'.$iter} = $1;
		$content =~ s/\bcase\s+\w+\.?\w*\s+when\b.*?\bend\b/_CASE_WHEN_$iter/is;
		$iter += 1;
    }
	return $source_content;
}

sub takeout_case_when_from_hash
{
	my $content = shift;
	
	my $iter = 1;
	foreach my $case_when_key (sort keys %$CASE_WHEN)
	{
		my $case_when_value = $CASE_WHEN->{'_CASE_WHEN_'.$iter};
		#$case_when_value = $MR->escape_regex_str($case_when_value);
		$content =~ s/_CASE_WHEN_$iter/$case_when_value/is;
		$iter += 1;
	}

	return $content;
}

sub blank
{
	my $ar = shift;
	my $sql = join("\n", @$ar);
	$MR->log_msg("blank:" . Dumper($ar));
	return "";
}


sub synapse_default_statement_handler
{
	my $ar = shift;
	return '' if $STOP_OUTPUT;
	my $sql = join("\n", @$ar);
	$MR->log_msg("synapse_default_statement_handler:" . Dumper($ar));
	if ($sql =~ /SET/ or $sql =~ /DECLARE/)
	{
		return ''; #if we haven't seen the BEGIN keyword, that means we are in the declaration segment. Skip it, as we'll handle it in the proc declaration handler
	}
	else
	{
		return $sql;
	}
}

sub replace_synapse_tables
{
	my $cont_str = shift;

	if ($CFG_POINTER->{catalog_file})
	{
		return $cont_str unless $CATALOG->{Synapse};
		foreach my $item (keys $CATALOG->{Synapse})
		{
			$cont_str = $MR->replace_single_pattern($cont_str,$item,$CATALOG->{Synapse}->{$item});
		}
	}
	return $cont_str;
}

# called by preprocess_routine hook
# modifies the content so that the converter can work with it
# the code has been prescanned already, so we know what the params are to the proc
sub process_PROC_START
{
	my $ar = shift;
	$MR->log_msg("process_PROC_START called");
	return '' if $STOP_OUTPUT;
	my $sql = join("\n", @$ar);
	
	my @ret = ();
	my %item_seen = ();
	foreach my $item(@PROCEDURE_PARAMS)
	{
		if ($CFG_POINTER->{set_lowercase})
		{
			$item =~ s/\b(\w+)\b/\L$1/gi;
		}
		next if $item_seen{$item};
		$item_seen{$item} = 1;
		push(@ret,'dbutils.widgets.text("'.$item.'", "")');
		push(@ret,$VARIABLE_PREFIX.$item.' = dbutils.widgets.get("'.$item.'")', "");
	}

	$MR->log_msg("process_PROC_START All Tables: " . Dumper($TABLES));
	if ($CFG_POINTER->{read_table_as_parquet})
	{
		foreach my $item (keys %$TABLES)
		{
			my $spark_sql_table = $CATALOG->{Databricks}->{$item};
			$MR->log_error("Table is not mapped in Databricks section: $item");
			my $par1 = $MR->replace_single_pattern($item,'.','_');
			my $par2 = $MR->replace_single_pattern($spark_sql_table,'.','/');
			
			push(@ret,"inputDF_lkp_$par1 = spark.read.parquet('/mnt/$par2/*')");
			push(@ret,"inputDF_lkp_$par1.createOrReplaceTempView('$par1')");
		}
    }
    

	my $proc_start = join("\n", @ret);
	$sql =~ s/PROC_START $PROCEDURE_NAME/$proc_start/;
	return code_indent($sql);
}

#gets called from preprocess sub
#separates SELECT statements by determining the level at which they are present.
#separation occurs by putting a delimiter in front of a legitimate SELECT statement
sub mark_separators
{
	my $sql = shift; #scalar content of file

	$sql =~ s/END\s*GO\s*$/${DELIM}\nPROC_FINISH/gis;
	$sql =~ s/END\s*$/${DELIM}\nPROC_FINISH/gis;
	$sql =~ s/with\s+RECOMPILE//gis; #so it does not mess up our WITH logic

	my $i = 0;
	my $len = length($sql);
	my @chars = split(//, $sql);
	my @final_chars = ();
	my $quote_escape_str = '__BBQUOTE_ESC@PE__';
	my $hit_cnt = 0;
	my $inside_1line_comment = 0; #single line comment flag
	my $inside_mline_comment = 0; #multi line comment flag
	my @prior_keywords = ('WHERE', 'GROUP BY', 'ORDER BY', 'IF', 'BEGIN', 'UPDATE', 'INSERT', 'MERGE', 'DECLARE', 'VALUES', 'UNION', 'VIEW');
	#my @curr_keywords_cond = ('CASE'); #capture conditionals.  We need to mark ELSE and END as COND_ELSE and COND_END
	my $prior_keyword = '';
	#my $prior_keyword_cond = '';
	my $level = 0;
	my $case_level = 0;
	my $case_hit_cnt = 0;
	my $with_used = 0;
	my @WITH_KW = qw(INSERT DELETE UPDATE);
	foreach my $c (@chars)
	{
		$inside_1line_comment = 1 if (!$inside_mline_comment && !$inside_1line_comment && substr($sql, $i, 2) eq '--');
		$inside_mline_comment = 1 if (!$inside_mline_comment && !$inside_1line_comment && substr($sql, $i, 2) eq '/*');
		$inside_mline_comment = 0 if ($inside_mline_comment && !$inside_1line_comment && substr($sql, $i, 2) eq '*/');
		$inside_1line_comment = 0 if (!$inside_mline_comment && $inside_1line_comment && substr($sql, $i, 1) eq "\n");
		$level++ if (!$inside_mline_comment && !$inside_1line_comment && substr($sql, $i, 1) eq "(");
		$level-- if (!$inside_mline_comment && !$inside_1line_comment && substr($sql, $i, 1) eq ")");

		#$MR->log_msg("MARK_SEP: NL at $i") if $c eq "\n";
		#$MR->log_msg("MARK_SEP: CR at $i") if $c eq "\r";

		#grab look for keywords
		if (!$inside_mline_comment && !$inside_1line_comment && $level == 0)
		{
			foreach my $kw (@prior_keywords)
			{
				my $tmp_str = substr($sql, $i-1, length($kw)+2 ); #grab 1 char before and after
				#$MR->log_msg("MARK_SEP: pos $i, KW $kw, STR: '$tmp_str'");
				if ($tmp_str =~ /\W$kw\W/gis)
				{
					#$MR->log_msg("MARK_SEP: KW_MATCH!");
					$prior_keyword = $kw;
				}
			}
		}

		my $tmp_with = substr($sql, $i-1, 6); #grab 1 char before and after
		if ($tmp_with =~ /\WWITH\W/gis && !$inside_mline_comment && !$inside_1line_comment && $level == 0 && !$with_used)
		{
			$with_used = 1;
			$MR->log_msg("WITH Found at level $level. Offset $i");
		}

		if ($with_used)
		{
			foreach my $wkw (@WITH_KW)
			{
				my $tmp_with_kw = substr($sql, $i-1, length($wkw)+2); #grab 1 char before and after
				#$MR->log_msg("WITH_KW: '$wkw', '$tmp_with_kw'");
				if ($tmp_with_kw =~ /\W$wkw\W/gis && !$inside_mline_comment && !$inside_1line_comment && $level == 0 && $with_used)
				{
					#$MR->log_msg("WITH KEYWORD Found at level $level. Offset $i. KW: $wkw");
					$with_used = 0;
					push(@final_chars, $WITH_PREFIX);
					last;
				}
			}
		}

		my $tmp_select = substr($sql, $i-1, 8); #grab 1 char before and after
		if ($tmp_select =~ /\WSELECT\W/gis)
		{
			$hit_cnt++;
			$MR->log_msg("MARK_SEP: SELECT. LEVEL: $level, 1L: $inside_1line_comment, ML: $inside_mline_comment, at pos $i, hit $hit_cnt. Prior: $prior_keyword. '$tmp_select'");
			if ( !$inside_mline_comment && !$inside_1line_comment && $level == 0 && $prior_keyword ne 'INSERT' && $prior_keyword ne 'UNION' && $prior_keyword ne 'VIEW')
			{
				$MR->log_msg("MARK_SEP: Adding delimiter!");
				push(@final_chars, "\n$DELIM\n");
			}
		}
		my $tmp_case = substr($sql, $i-1, 6); #grab 1 char before and after
		if ($tmp_case =~ /\WCASE\W/gis && !$inside_mline_comment && !$inside_1line_comment)
		{
			$case_level++;
			$case_hit_cnt++;
			$MR->log_msg("MARK_SEP: CASE. LEVEL: $case_level, 1L: $inside_1line_comment, ML: $inside_mline_comment, at pos $i, hit $case_hit_cnt.");
		}


		#Handle ELSE keyword, which could be inside a case statement or at inside a conditional
		my $tmp_else = substr($sql, $i-1, 6); #grab 1 char before and after
		if ($tmp_else =~ /\WELSE\W/gis && !$inside_mline_comment && !$inside_1line_comment)
		{
			if ($case_level > 0)
			{
				$MR->log_msg("MARK_SEP: CASE ELSE. LEVEL: $case_level, 1L: $inside_1line_comment, ML: $inside_mline_comment, at pos $i, hit $case_hit_cnt.");
				#$case_level--; #we are closing a case statement
			}
			else
			{
				push(@final_chars, "\n${DELIM}\nCOND_"); #make it COND_ELSE
				$MR->log_msg("MARK_SEP: CONDITIONAL ELSE. 1L: $inside_1line_comment, ML: $inside_mline_comment, at pos $i, hit $case_hit_cnt.");
			}
		}


		#Handle END keyword, which could be inside a case statement or at the end of a conditional
		my $tmp_end = substr($sql, $i-1, 5); #grab 1 char before and after
		if ($tmp_end =~ /\WEND\W/gis && !$inside_mline_comment && !$inside_1line_comment)
		{
			if ($case_level > 0)
			{
				$MR->log_msg("MARK_SEP: CASE END. LEVEL: $case_level, 1L: $inside_1line_comment, ML: $inside_mline_comment, at pos $i, hit $case_hit_cnt.");
				$case_level--; #we are closing a case statement
			}
			else
			{
				# push(@final_chars, "\n${DELIM}\nCOND_"); #make it COND_END
				$MR->log_msg("MARK_SEP: CONDITIONAL END. 1L: $inside_1line_comment, ML: $inside_mline_comment, at pos $i, hit $case_hit_cnt.");
			}
		}
		
		my $tmp_if = substr($sql, $i-1, 4); #grab 1 char before and after to check for IF
		if ($tmp_if =~ /\WIF\W/is && !$inside_mline_comment && !$inside_1line_comment && $level == 0)
		{
			push(@final_chars, "\n$DELIM\n");
		}

		push(@final_chars, $c) unless $c eq '';
		$i++;
	}
	$sql = join('',@final_chars);
	return $sql;
}

#adjusts the initial content and plus in delimiters
sub synapse_preprocess
{
	my $cont = shift;

	@FRAGMENT_COMMENTS_SORTED = ();
	
	#$MR->log_msg("CONT CHECK 100 PREPROCESS: " . Dumper($cont));

	#my @cont = split("\n", $cont);
	foreach my $ln (@$cont)
	{
		if ($ln =~ /(\-\-.*\'.*$)/p)
		{
			my ($prematch, $match, $postmatch) = (${^PREMATCH}, ${^MATCH}, ${^POSTMATCH});
			$MR->log_msg("Found quote inside an inline comment: $match");
			$match =~ s/\'/ /g;
			$ln = $prematch . $match . $postmatch;
			$MR->log_msg("Changed line to $ln");
		}
	}
	#$MR->log_msg("Dumper content: " . Dumper(\@cont));
	#$cont = join("\n", @cont);
	$MR->log_msg("Preprocessing file");
	my @ret = ();

	my $cont_str = join("\n",@$cont);
	$cont_str =~ s/\s*\-\-.*$//gm unless $CFG_POINTER->{keep_comments_in_place};
	$cont_str =~ s/\/\*.*?\*\///gs unless $CFG_POINTER->{keep_comments_in_place};



	my @comments = capture_comments($cont_str);
	my @static_strings = capture_static_strings($cont_str);

	if ($CFG{keep_comments_in_place})
	{
		my $comm_idx = 0;

		@FRAGMENT_COMMENTS_SORTED = @comments;
		#sort by length, largest first
		@FRAGMENT_COMMENTS_SORTED = sort { length($b) <=> length($a) } @FRAGMENT_COMMENTS_SORTED;

		foreach my $comment (@FRAGMENT_COMMENTS_SORTED)
		{
			my $replacement = "__BB_COMMENT_" . $comm_idx . "__";
			$cont_str =~ s/\Q$comment\E/$replacement\n/s;
			$comm_idx++;
		}
	}
	
		my $str_idx = 0;

	{

		#sort by length, largest first
		@static_strings = sort { length($b) <=> length($a) } @static_strings;

		foreach my $static_string (@static_strings)
		{
			my $replacement = "__bb_static_string_" . $str_idx . "__";
			$cont_str =~ s/\Q$static_string\E/$replacement/s;
			$str_idx++;
		}
	}
	$cont_str =~ s/\bIF\s+OBJECT_ID.*?\bIS\s+NOT\s+NULL\s+DROP TABLE.*?$//gim;

	if ($CFG_POINTER->{set_lowercase})
	{
		$cont_str =~ s/\b(\w+)\b/\L$1/gi;
	}
	$str_idx = 0;
	foreach my $static_string (@static_strings)
	{
		my $replacement = "__bb_static_string_" . $str_idx . "__";
		$cont_str =~ s/\Q$replacement\E/$static_string/s;
		$str_idx++;
	}
	
	$cont_str =~ s/^(\s*IF.*?)\bSET\b(.*)/$1\nBEGIN\nSET$2\nEND\n/gim;

	#$MR->log_msg("CONT CHECK 101 PREPROCESS: $cont_str");
	#$MR->log_error($cont_str);


	$cont_str = mark_separators($cont_str);


	#$cont_str =~ s/\bAS\b(.*?)\bBEGIN\b/\nAS\nBEGIN\n/gis;
	#$cont_str =~ s/\bAS\b(.*?)\bBEGIN\b/\nAS\nBEGIN\n/is;
	print "NEW CONT 01:\n$cont_str\n***********\n";
	$cont_str =~ s/CREATE\s+PROC\b/CREATE PROCEDURE/gis;

			#$MR->log_error($cont_str);


	if (!$CFG_POINTER->{do_not_use_proc_start} and $cont_str =~ /CREATE\s+PROCEDURE\s+(\[\w+\]\.\[\w+\])(.*?)AS\b/gisp) #substitue proc declaration with PROC_START. We will handle it in a fragment handler
	{
		
		my ($prematch, $match, $postmatch) = (${^PREMATCH}, ${^MATCH}, ${^POSTMATCH});
		my $tmp_proc_nm = $1;
		$MR->log_msg("Found procedure declaration, plugging in PROC_START");
		$PROCEDURE_NAME = $tmp_proc_nm;
		$PROCEDURE_NAME =~ s/\[//g;
		$PROCEDURE_NAME =~ s/\]//g;
		
		if ($postmatch && $MR->trim($postmatch) ne '')
		{
			$cont_str = "PROC_START $PROCEDURE_NAME\n$DELIM\n$postmatch";
        }
		else
		{
			$cont_str = "PROC_START $PROCEDURE_NAME\n$DELIM\n$prematch";
		}
	}

	$cont_str = process_columns($cont_str) if $CFG_POINTER->{process_square_bracket_columns};
	

	if (!$CFG_POINTER->{do_not_use_proc_start})
	{
		$cont_str =~ s/SET\s+\@(\w+)\s*\=/$DELIM\nSELECT \@$1\=/gis;
	}
	else
	{
		$cont_str =~ s/SET\s+\@(\w+)\s*\=/$DELIM\n__S3T__ \@$1\=/gis;
	}
	my @keywords = ("BULK INSERT", "DELETE", "INSERT", "UPDATE","WITH____DELETE", "WITH____INSERT", "WITH____UPDATE", "MERGE", "DECLARE", "BEGIN", "EXEC", "EXECUTE", "TRUNCATE","WHILE","PRINT","CREATE");
	my $first_state = 1;

	
	$cont_str = replace_synapse_tables($cont_str);

	$cont_str =~ s/\bTHEN\b\s+\bINSERT\b/INSERT_IN_MERGE/gim;
	$cont_str =~ s/\bTHEN\b\s+\bUPDATE\b/UDPATE_IN_MERGE/gim;
	$cont_str =~ s/\bTHEN\b\s+\bDELETE\b/DELETE_IN_MERGE/gim;

	foreach my $kw (@keywords)
	{
		$cont_str =~ s/^\s*$kw\b/\n$DELIM\n$kw/gim;
	}
	$cont_str =~ s/(\bWITH\b\s+.*?\s+\bAS\b\s+\()/\n$DELIM\n$1/gim;

	if($CFG_POINTER->{if_end} and $CFG_POINTER->{if_end} == 1)
	{
		$cont_str =~ s/\bCOND_END\s+\;\s*COND_ELSE/ENDELSE/gim;
	}
	
	$cont_str =~ s/INSERT_IN_MERGE/ THEN\nINSERT /gim;
	$cont_str =~ s/UDPATE_IN_MERGE/ THEN\nUPDATE /gim;
	$cont_str =~ s/DELETE_IN_MERGE/ THEN\nDELETE /gim;
	#$cont_str =~ s/(declare\s.*?)\n(\bselect\b)/$1\n$DELIM\n$2/gis; #separate DECLARE from SELECT
	#$cont_str =~ s/(\bselect\b\s+@\w+\s+=)/\n$DELIM\n$1\n$DELIM/gis; #separate SELECT @variable
	$cont_str = collect_case_when_in_hash($cont_str,$cont_str);
	
	$cont_str =~ s/\bEND\b/\n$DELIM\nCOND_END\n$DELIM/gis;
	$cont_str =~ s/$DELIM\n$DELIM/$DELIM/gis;
	#$cont_str =~ s/PROC_FINISH//gis;
	$cont_str = takeout_case_when_from_hash($cont_str);

	$cont_str =~ s/$WITH_PREFIX//gim;

	# my @WITH_KW = qw(INSERT DELETE UPDATE);
	# foreach my $wkw (@WITH_KW)
	# {
	# 	$cont_str =~ s/$WITH_PREFIX_//gis;
	# }
	$cont_str =~ s/\s*\;\s*\;/;/gis;
	$cont_str =~ s/^\s*GO\s*$/;\n/gim;
	$cont_str =~ s/(\w+)\s+SET\s+NOCOUNT\s+(ON|OFF)/$1/gis;
	$cont_str =~ s/\[//gs unless $CFG_POINTER->{keep_square_brackets};
	$cont_str =~ s/\]//gs unless $CFG_POINTER->{keep_square_brackets};
	$cont_str =~ s/\b(DROP\s+TABLE\b\s+\#*\w+)/\n$DELIM\n$1/gis;
	$cont_str =~ s/(\bCREATE\s+VIEW\s+\w+\.?\w*\.?\w*\s+\bAS)\s*\;/$1/gis;
	$cont_str = add_cond_end_after_oneline_condition($cont_str);
	#$MR->log_error($cont_str);

	foreach my $t (keys %REPLACE_TABLES)
	{
		$cont_str =~ s/$t/$REPLACE_TABLES{$t}/gi;
	}
	#special handling for SELECTs that were not handled earlier.  Need to separate them out
	my @sc_kw = ("GROUP BY", "ORDER BY"); #if any of these are followed by SELECT and it is on the same level (i.e. it is not a sub-query, then add the delimiter)
	my $matched_flag = 0;
	my $SELECT_SUBST = '__S3L3CT__'; #use this temporarily to avoid additional looping.  At the end of the loop substitute it to SELECT
	my $total_hits = 0;
	@ret = (@ret,split(/\n/, $cont_str));

	return @ret;
}

# Main subroutine to process columns with brackets
sub process_columns
{
    my ($input_string) = @_;

    # Regex to identify the columns
    $input_string =~ s/\[(.*?)\]/'[' . replace_special_characters($1) . ']'/ge;

    return $input_string;
}

# Helper subroutine to replace spaces with underscores and remove other special characters
sub replace_special_characters
{
    my ($column_name) = @_;

    # Replace spaces with underscores
    $column_name =~ s/\s+/_/g;

    # Remove other special characters except underscores and alphanumeric characters
    $column_name =~ s/[^\w_]//g;

    return $column_name;
}

sub add_cond_end_after_oneline_condition
{
	my $content = shift;
	$MR->log_msg("add_cond_end_after_oneline_condition :\n$content");
	
	my @matches = $content =~ /IF\s+EXISTS.*?$DELIM\s*(.*?$DELIM)/gis;
	my @matches1 = $content =~ /IF\s+OBJECT_ID.*?$DELIM\s*(.*?$DELIM)/gis;
	@matches = (@matches, @matches1);
	my %match_hash = map { $_ => 1 } @matches;
	
	foreach my $pattern (keys %match_hash)
	{
		if ($pattern !~ /\bBEGIN\b/is)
		{
			my $escaped_pattern = $MR->escape_regex_str($pattern);
			$content =~ s/$escaped_pattern/$pattern\nCOND_END$DELIM\n/gis;
		}
	}
	return $content;
}

sub read_dml
{
	my $ar = shift;
	#return '' if $STOP_OUTPUT;
	my $sql = join("\n", @$ar);
	$MR->log_msg("read_dml :\n$sql");
	
	my $ret = $CONVERTER->convert_sql_fragment($MR->trim($sql));
	my $table_name = $PROCEDURE_NAME;
	my $table_template = $CFG_POINTER->{commands}->{select_into_table_template};
	if ($sql =~ /\bINTO\s+\#(\w+)/is)
	{
		$table_name = $1;
		$TEMP_TABLES{$table_name} = 1;
		$ret =~ s/\bINTO\b\s+\#\w+\s+//gs;
		$table_template = $CFG_POINTER->{commands}->{select_into_pound_table_template};
	}
	else
	{
		$table_template = $CFG_POINTER->{commands}->{select_into_table_template};
	}
	$table_template =~ s/\%TABLE_NAME%/$CFG_POINTER->{temp_table_prefix}$table_name/gs;
	$ret =~ s/^\s*\;\s*$//gim;
	
	if (!$CFG_POINTER->{commands}->{select_into_table_template})
	{
		$ret =~ s/^\s*(SELECT.*?)\bINTO\b(.*?)(\bFROM\b.*)/CREATE OR REPLACE TEMP VIEW $2 AS\n$1$3/is;
    }
	
	$ret = replace_params_as_spark($table_template.$ret, undef, 'query_'.$QUERY_INCREMENT);

	$ret =~ s/__BB_COMMENT_([0-9]+)__/__BB_COMMENT_SPARK_$1__/gis;

	$ret = 'spark.sql(' . $ret . ')';

	if ($CFG_POINTER->{commands}->{select_into_pound_table_suffix_template})
	{
		$ret .= "\nquery_" . $QUERY_INCREMENT . $CFG_POINTER->{commands}->{select_into_pound_table_suffix_template} 
		        . "('query_" . $QUERY_INCREMENT . "')";
	}

    
	$QUERY_INCREMENT += 1;
	return code_indent($ret) . "\n";
}

sub create_view
{
	my $ar = shift;
	#return '' if $STOP_OUTPUT;
	my $sql = join("\n", @$ar);
	$MR->log_msg("create_view :\n$sql");
	
	my $ret = $CONVERTER->convert_sql_fragment($MR->trim($sql));

	$ret =~ s/^\s*\;\s*$//gim;
	
	if ($ret =~ /\bCREATE\s+VIEW\b\s+.*?\s+\bAS\b.*/is)
	{
       $ret =~ s/\bCREATE\s+VIEW\b\s+(.*?)\s+\bAS\b(.*)/CREATE OR REPLACE TEMP VIEW $1 AS\n$2/is;
    }
    elsif (!$CFG_POINTER->{commands}->{select_into_table_template})
	{
		$ret =~ s/^\s*(SELECT.*?)\bINTO\b(.*?)(\bFROM\b.*)/CREATE OR REPLACE TEMP VIEW $2 AS\n$1$3/is;
    }
	
	#$ret = replace_params_as_spark($ret, undef, 'query_'.$QUERY_INCREMENT);

	$ret =~ s/__BB_COMMENT_([0-9]+)__/__BB_COMMENT_SPARK_$1__/gis;

	$ret = 'spark.sql("""' . $ret . '""")';

	#if ($CFG_POINTER->{commands}->{select_into_pound_table_suffix_template})
	#{
	#	$ret .= "\nquery_" . $QUERY_INCREMENT . $CFG_POINTER->{commands}->{select_into_pound_table_suffix_template} 
	#	        . "('query_" . $QUERY_INCREMENT . "')";
	#}

    
	$QUERY_INCREMENT += 1;
	return code_indent($ret) . "\n";
}

sub read_catalog_file
{
	my $f = $CFG_POINTER->{catalog_file};
	if (!$f)
	{
        return;
    }
	
	if(!open(IN, '<' . $MR->get_utf8_encoding_spec(), $f))
	{
		$MR->log_error("********** ERROR ***********");
		$MR->log_error("Cannot open file $f for reading: $!");

		my $mess = longmess();
		$MR->debug_msg("read_file_content Stack trace for $f:\n" . Dumper( $mess ));
	}
	
	while(my $ln = <IN>)
	{
		chomp($ln);
		$ln =~ s/\n//g;
		$ln =~ s/\r//g;
		if ($ln && $ln ne '')
		{
			my @key_val = split(/\|/,$ln);
			if ($#key_val == 1)
			{
				$REPLACE_TABLES{$key_val[0]} = $key_val[1];
            }
		}
	}
	close(IN);	
}

sub convert_print
{
	my $ar = shift;
	#return '' if $STOP_OUTPUT;
	my $sql = join("\n", @$ar);
	$MR->log_msg("convert_print :\n$sql");

	my $to_print = "__UNKNOWN_VALUE__";
	$to_print = $2 if $sql =~ /PRINT\s+('|\")(.*)\1/is;

	my $print_template = $CFG_POINTER->{commands}->{print_template};
	$print_template =~ s/\%TEXT%/$to_print/gs;

	return code_indent($print_template);
}

sub convert_exists
{
	my $ar = shift;
	#return '' if $STOP_OUTPUT;
	my $sql = join("\n", @$ar);
	$MR->log_msg("convert_exists :\n$sql");

	my $ret = $CONVERTER->convert_sql_fragment($MR->trim($sql));

	my $table_name = "__UNKNOWN_TABLE__";
	$table_name = $1 if $ret =~ /N'([\w\.]+)'/is;
	my $table_template = $CFG_POINTER->{commands}->{exists_table_template};
	$table_template =~ s/\%TABLE_NAME%/$table_name/gs;

	if ($ret =~ /\bIF\s+NOT\s+EXISTS\b/is)
	{
		$table_template =~ s/\%NOT%/not /gs;
	}
	else
	{
		$table_template =~ s/\%NOT%//gs;
	}

	$ret = $table_template;

	return $ret;
}

sub convert_with
{
	my $ar = shift;
	#return '' if $STOP_OUTPUT;
	my $sql = join("\n", @$ar);
	$MR->log_msg("convert_with :\n$sql");
	
	my $ret = $CONVERTER->convert_sql_fragment($MR->trim($sql));
	if ($ret =~ /\bINTO\s+\#(\w+)/is)
	{
		my $table_name = $1;
		$TEMP_TABLES{$table_name} = 1;
		$ret =~ s/\bINTO\b\s+\#\w+\s+//gs;
		my $table_template = $CFG_POINTER->{commands}->{select_into_pound_table_template};
		$table_template =~ s/\%TABLE_NAME%/$table_name/gs;
		$ret = $table_template.$ret;
	}
	
	$ret = replace_params_as_spark($ret, undef, 'query_'.$QUERY_INCREMENT);

	$ret =~ s/__BB_COMMENT_([0-9]+)__/__BB_COMMENT_SPARK_$1__/gis;

	$ret = 'query_'.$QUERY_INCREMENT.' = spark.sql(' . $ret . ')';
	$QUERY_INCREMENT += 1;
	return code_indent($ret) . "\n";	
}

sub top_x_to_limit #changes SELECT TOP n ... to SELECT ... LIMIT n.  The challenge is that the SELECTs can be nested
{
		my $str = shift; #scalar content
		$MR->log_msg("top_x_to_limit: $str");
		while( $str =~ /SELECT\s+TOP\s+([0-9]+)/gisp )
		{
			my ($prematch, $match, $postmatch) = (${^PREMATCH}, ${^MATCH}, ${^POSTMATCH});
			my $limit = $1;
			my $pre_len = length($prematch);
			my $match_len = length($match);
			my $post_len = length($postmatch);
			$MR->log_msg("top_x_to_limit: Found $match at position $pre_len, LIMIT set to $limit");

			#go through postmatch and find the end of it or the closing parenthesis and plug the LIMIT clause there
			my @chars = split(//, $postmatch);
			my $inside_1line_comment = 0; #single line comment flag
			my $inside_mline_comment = 0; #multi line comment flag
			my $level = 0;
			my $i = 0;
			foreach my $c (@chars)
			{
				if (!$inside_mline_comment && !$inside_1line_comment && substr($postmatch, $i, 2) eq '--')
				{
					$inside_1line_comment = 1;
				}
				if (!$inside_mline_comment && !$inside_1line_comment && substr($postmatch, $i, 2) eq '/*')
				{
					$inside_mline_comment = 1;
				}
				if ($inside_mline_comment && !$inside_1line_comment && substr($postmatch, $i, 2) eq '*/')
				{
					$inside_mline_comment = 0;
				}
				if (!$inside_mline_comment && $inside_1line_comment && substr($postmatch, $i, 1) eq "\n")
				{
					$inside_1line_comment = 0;
				}
				if (!$inside_mline_comment && !$inside_1line_comment && substr($postmatch, $i, 1) eq "(")
				{
					$level++;
				}
				if (!$inside_mline_comment && !$inside_1line_comment && substr($postmatch, $i, 1) eq ")")
				{
					$level--;
				}
				if ($level < 0)
				{
					$MR->log_msg("top_x_to_limit: LEVEL is $level at postmatch position $i. 10 chars: " . substr($postmatch,$i, 10));
					$postmatch = substr($postmatch,0,$i) . "\nLIMIT $limit " . substr($postmatch,$i);
					last;
				}
				$i++;
			}

			$str = $prematch . "SELECT " . $postmatch;
		}
		return $str;
}

sub convert_if_start
{
	my $ar = shift;
	my $sql = join("\n", @$ar);
	$MR->log_msg("convert_if_start:\n$sql");
	my $ret = $CONVERTER->convert_sql_fragment($MR->trim($sql));

	$ret =~ s/\@/$VARIABLE_PREFIX/gis;
	$ret =~ s/\s*;\s*$//gis;
	$ret =~ s/--.*//gim;
	$ret =~ s/\bIS\b/is/gi;
	$ret =~ s/\bNULL\b/None/gi;
	$ret =~ s/\bNOT\b/not/gi;
	$ret = $MR->trim($ret);
	$ret =~ s/\bif\b/if/i;
	chomp($ret);
	$ret = code_indent($ret);
	$ret =~ s/\s*$/\:/gis;
	$INDENT++;
	return $ret;
}

sub convert_end_if
{
	my $ar = shift;
	my $sql = join("\n", @$ar);
	$MR->log_msg("convert_end_if:\n$sql");
	
	$INDENT--;
	if ($INDENT < 0)
	{
        $INDENT = 0;
		return '';
    }
    else
	{
		my $ret = code_indent("# Decreased INDENT");
		#$ret =~ s/\s*$/\:/gis;
		return $ret;
	}
}

sub convert_else_start
{
	my $ar = shift;
	my $sql = join("\n", @$ar);
	$MR->log_msg("convert_else_start:\n$sql");
	my $ret = $CONVERTER->convert_sql_fragment($MR->trim($sql));
	$ret =~ s/\@/$VARIABLE_PREFIX/gis;
	$ret =~ s/\s*;\s*$//gis;
	$ret =~ s/--.*//gim;
	$ret = $MR->trim($ret);
	chomp($ret);
	$ret =~ s/\bCOND_ELSE\b/else/i;
	$ret = code_indent($ret);
	$ret =~ s/\s*$/\:/gis;
	$INDENT++;
	return $ret;
}

sub convert_start_while
{
	my $ar = shift;
	my $sql = join("\n", @$ar);
	$MR->log_msg("convert_start_while:\n$sql");
	my $ret = $CONVERTER->convert_sql_fragment($MR->trim($sql));
	$ret =~ s/\@/$VARIABLE_PREFIX/gis;
	$ret =~ s/WHILE/while/gis;
	$ret =~ s/\s*;\s*$//gis;
	$ret =~ s/--.*//gim;
	$ret =~ s/\bIS\b/is/gi;
	$ret =~ s/\bNULL\b/None/gi;
	$ret =~ s/\bNOT\b/not/gi;
	$ret = $MR->trim($ret);
	chomp($ret);
	$ret = code_indent($ret);
	$ret =~ s/\s*$/\:/gis;
	$INDENT++;
	return $ret;
}

sub convert_if_exists
{
	my $ar = shift;
	my $sql = join("\n", @$ar);
	$MR->log_msg("covert_if_exists:\n$sql");
	my $ret = $CONVERTER->convert_sql_fragment($MR->trim($sql));
	$ret =~ s/\@(\w+)/'{$VARIABLE_PREFIX$1}'/gis;
	$ret =~ /\bIF\s+EXISTS\s*\((.*?)\)/is;
	my $query = $MR->trim($1);
	if ($query =~ /\bselect\b.*?sys\.objects.*?OBJECT_ID\(N?(\'.*?\')/is)
	{
        $ret = code_indent("if spark.catalog.tableExists($1):\n");
    }
    else
	{
		$query =~ s/__BB_COMMENT_([0-9]+)__/__BB_COMMENT_SPARK_$1__/gis;

		$ret = code_indent("result = spark.sql(f\"\"\"$query\"\"\")\nif not result.isEmpty():\n");
	}

	$INDENT++;
	return $ret;
}

sub convert_update_from
{
	my $ar = shift;
	my $sql = join("\n", @$ar);
	$MR->log_msg("convert_update_from:\n$sql");
	my $ret = $CONVERTER->convert_sql_fragment($MR->trim($sql));
	$ret =~ s/\@(\w+)/'{$VARIABLE_PREFIX$1}'/gis;
	$ret = $CONVERTER->convert_update_to_merge($ret);
	$ret =~ s/\;\s*$//gis;

	$ret =~ s/__BB_COMMENT_([0-9]+)__/__BB_COMMENT_SPARK_$1__/gis;

	$ret = code_indent("spark.sql(f\"\"\"$ret\"\"\")\n");

	return $ret;	
}

sub convert_update_table
{
	my $ar = shift;
	my $sql = join("\n", @$ar);
	$MR->log_msg("convert_update_table:\n$sql");
	$sql = $MR->trim($sql);
	$sql =~ s/(.*)\;\s*$/$1/s;
	$sql = $MR->trim($sql);
	my $ret = $CONVERTER->convert_sql_fragment($sql);
	$ret =~ s/\@(\w+)/'{$VARIABLE_PREFIX$1}'/gis;
	
	#my $ret = $CONVERTER->convert_sql_fragment($sql);
	$ret =~ s/__BB_COMMENT_([0-9]+)__/__BB_COMMENT_SPARK_$1__/gis;

	$ret = code_indent("spark.sql(f\"\"\"$ret\"\"\")\n");

	return $ret;
}

sub convert_execute
{
	my $ar = shift;
	my $sql = join("\n", @$ar);
	$MR->log_msg("convert_execute:\n$sql");
	$sql =~ s/\bEXECUTE\s+//s;
	$sql =~ s/\bEXEC\s+//s;
	$sql =~ s/(.*)\;$/$1/s;
	$sql = $MR->trim($sql);
	$sql =~ /(.*?)\s+(.*)/;
	my $proc_name = $1;
	my $proc_params = $MR->trim($2);
	if (!$proc_params)
	{
        return code_indent("dbutils.notebook.run(\"$proc_name\", 60)");
    }
	elsif($proc_params !~ /\=/s)
	{
		my @params = split /\,/, $proc_params;
		my $arguments = '{';
		my $index = 1;
		foreach my $param (@params)
		{
			if ($arguments ne '{')
			{
                $arguments .= ',';
            }
            $arguments .= "\"argument$index\"\: $param";
			$index += 1;
		}
		$arguments .= '}';
		return code_indent("dbutils.notebook.run(\"$proc_name\", 60, $arguments)");
	}
	else
	{
		my @params = split /\,/, $proc_params;
		my $arguments = '{';
		foreach my $param (@params)
		{
			if ($arguments ne '{')
			{
                $arguments .= ',';
            }

			$param =~ /(.*?)\=(.*)/s;
			my $arg_name = $MR->trim($1);
			my $arg_value = $MR->trim($2);
            $arguments .= "\"$arg_name\"\: $arg_value";
		}
		return code_indent("dbutils.notebook.run(\"$proc_name\", 60, $arguments)");
	}
}

sub convert_drop_table
{
	my $ar = shift;
	my $sql = join("\n", @$ar);
	$MR->log_msg("convert_drop_table:\n$sql");
	$sql =~ s/(.*)\;$/$1/s;
	my $ret = $CONVERTER->convert_sql_fragment($sql);
	$ret =~ s/__BB_COMMENT_([0-9]+)__/__BB_COMMENT_SPARK_$1__/gis;
	$ret = $MR->trim($ret);

	return code_indent("spark.sql(f\"\"\"$ret\"\"\")\n");
}

sub convert_alter_table
{
	my $ar = shift;
	my $sql = join("\n", @$ar);
	$MR->log_msg("convert_alter_table:\n$sql");
	$sql =~ s/(.*)\;$/$1/s;
	my $ret = $CONVERTER->convert_sql_fragment($MR->trim($sql));
	$ret =~ s/\bADD\b/ADD columns (/gis;
	$ret .=')';
	#my $ret = $CONVERTER->convert_sql_fragment($MR->trim($sql));
	$ret =~ s/__BB_COMMENT_([0-9]+)__/__BB_COMMENT_SPARK_$1__/gis;

	return code_indent("spark.sql(f\"\"\"$ret\"\"\")\n");
}

sub convert_merge_into
{
	my $ar = shift;
	my $sql = join("\n", @$ar);
	$MR->log_msg("convert_merge_into:\n$sql");
	$sql =~ s/(.*)\;$/$1/s;
	my $ret = $MR->trim($sql);
	$ret =~ s/\bMERGE\b/MERGE INTO/gis;
	if($ret =~ /(\bMERGE INTO\b.*?)(\s*\bWHEN NOT MATCHED.*?)(\s*\bWHEN MATCHED.*)/is)
	{
		$ret = $1.$3.$2;
	}
	#my $ret = $CONVERTER->convert_sql_fragment($MR->trim($sql));
	#$ret =~ s/__BB_COMMENT_([0-9]+)__/__BB_COMMENT_SPARK_$1__/gis;
	$ret =~ s/\@(\w+)/'{$VARIABLE_PREFIX$1}'/g;
	$ret = $CONVERTER->convert_sql_fragment($ret);
	return code_indent("spark.sql(f\"\"\"$ret\"\"\")\n");
}

sub from_to_substitution
{
	my $array_string = shift;
	my $expression = shift;

	my @token_substitutions = @{$array_string};
	foreach my $token_sub (@token_substitutions)
	{
		my ($from, $to) = ($token_sub->{from}, $token_sub->{to});
		if ($expression =~ /$from/is)
		{
			while ($expression =~ s/$from/$to/is)
			{
				my @tokk = ($1,$2,$3,$4,$5,$6,$7,$8,$9);
				my $idxx = 1;
				foreach my $too (@tokk)
				{
					$expression =~ s/\$$idxx/$too/g;
					$idxx++;
				}
			}
		}
	}

	return $expression;
}