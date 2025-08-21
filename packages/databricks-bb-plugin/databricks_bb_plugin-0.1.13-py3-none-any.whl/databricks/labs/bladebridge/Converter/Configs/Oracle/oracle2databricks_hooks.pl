use strict;
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
########################
		$tbl =~ s/\)//;
########################
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
# sub prescan_code_mssql
sub prescan_code_oracle
{
	my $filename = shift;
	my $obj = shift;
	
	$CATALOG = $MR->read_json_config($obj->{object_catalog});
	$PROCEDURE_NAME = substr($filename,rindex($filename,'\\')+1,rindex($filename,'.') - rindex($filename,'\\')-1);
	$TABLES = {};
	get_all_tables($filename);
	print "******** prescan_code_oracle $filename *********\n";
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
	$cont =~ s/\bAS\b(.*?)\bBEGIN\b/\nAS\nBEGIN\n/gis;
	if ($cont =~ /CREATE\s+PROCEDURE\s+\[\w+\]\.\[\w+\](.*)AS\s+BEGIN/gis)
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
			push(@INTERNAL_PARAMS, $matched[0]);
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
	
	$DELIM = $CFG_POINTER->{code_fragment_breakers}->{line_end}->[0];
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
	if ($sql =~ /DECLARE\s+\@(\w+)\s+TABLE/gis)
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

	$ret = 'query_'.$QUERY_INCREMENT.' = spark.sql(' . $ret . ')';
	
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
				$script = $MR->replace_single_pattern($script,'@'.$item, "'{".$item."}'");
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
		$script = '"""' . $script . '"""'.$format_text;
	}
	else
	{
		if($is_assignment == 1)
		{
			$script = 'SELECT '. $script;
		}
		$script = '"""' . $script . '"""';
	}
	
	#do the final sweep and remove any @table_var references - replace with just variable
	foreach my $tbl (keys %TABLE_VARS)
	{
		$script =~ s/\@$tbl\b/$tbl/gis;
	}

	return $script;
}

sub convert_var_assignment
{
	my $ar = shift;
	#return '' if $STOP_OUTPUT;
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
		my $ret = $CONVERTER->convert_sql_fragment($MR->trim($stmt));
		$ret =~ s/\;\s*$//gis; #get rid of the trailing semicolon
		$ret = replace_params_as_spark($ret, $is_assignment, "assignment for $df_name");
		$ret = $df_name . ' = spark.sql(' . $ret . ')' . "\n$VARIABLE_PREFIX$var = $df_name." . 'collect()[0][0]';
		
		return code_indent($ret) . "\n";	
	}
	else
	{
		return "!!!!!!! Cannot match pattern in convert_var_assignment for $sql!";
	}
}

sub blank
{
	my $ar = shift;
	my $sql = join("\n", @$ar);
	$MR->log_msg("blank:" . Dumper($ar));
	return "";
}


sub mssql_default_statement_handler
{
	my $ar = shift;
	return '' if $STOP_OUTPUT;
	my $sql = join("\n", @$ar);
	$MR->log_msg("mssql_default_statement_handler:" . Dumper($ar));
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
	return $cont_str unless $CATALOG->{Synapse};
	foreach my $item (keys $CATALOG->{Synapse})
	{
		$cont_str = $MR->replace_single_pattern($cont_str,$item,$CATALOG->{Synapse}->{$item});
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
		next if $item_seen{$item};
		$item_seen{$item} = 1;
		push(@ret,'dbutils.widgets.text("'.$item.'", "")');
		push(@ret,$VARIABLE_PREFIX.$item.' = dbutils.widgets.get("'.$item.'")', "");
	}

	$MR->log_msg("process_PROC_START All Tables: " . Dumper($TABLES));

	my $spark_read_type = "spark.read.parquet";   # Default
	$spark_read_type = $CFG{spark_read_type} if ($CFG{spark_read_type});
	foreach my $item (keys %$TABLES)
	{
		my $spark_sql_table = $CATALOG->{Databricks}->{$item};
		$MR->log_error("Table is not mapped in Databricks section: $item");
		my $par1 = $MR->replace_single_pattern($item,'.','_');
		my $par2 = $MR->replace_single_pattern($spark_sql_table,'.','/');
		
		# push(@ret,"inputDF_lkp_$par1 = spark.read.parquet('/mnt/$par2/*')");
		push(@ret,"inputDF_lkp_$par1 = $spark_read_type('/mnt/$par2/*')");
		push(@ret,"inputDF_lkp_$par1.createOrReplaceTempView('$par1')");
	}
	my $proc_start = join("\n", @ret);
##################
	# $sql =~ s/PROC_START $PROCEDURE_NAME/$proc_start/;)
	$sql =~ s/^/$proc_start\n/;
#############
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
	my @prior_keywords = ('WHERE', 'GROUP BY', 'ORDER BY', 'IF', 'BEGIN', 'UPDATE', 'INSERT', 'MERGE', 'DECLARE', 'VALUES', 'UNION');
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
			if ( !$inside_mline_comment && !$inside_1line_comment && $level == 0 && $prior_keyword ne 'INSERT' && $prior_keyword ne 'UNION')
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
				push(@final_chars, "\n${DELIM}\nCOND_"); #make it COND_END
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
# sub mssql_preprocess
sub oracle_preprocess
{
	my $cont = shift;
#######
	if ($CFG{object_catalog_processing})
	{
		my $sql = process_PROC_START($cont);
		@$cont = split(/\n/, $sql);
	}
########
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
	#$MR->log_msg("CONT CHECK 101 PREPROCESS: $cont_str");
	$cont_str = mark_separators($cont_str);

	#$cont_str =~ s/\bAS\b(.*?)\bBEGIN\b/\nAS\nBEGIN\n/gis;
	$cont_str =~ s/\bAS\b(.*?)\bBEGIN\b/\nAS\nBEGIN\n/is;
	print "NEW CONT 01:\n$cont_str\n***********\n";

	if ($cont_str =~ /CREATE\s+PROCEDURE\s+(\[\w+\]\.\[\w+\])(.*?)AS\s+BEGIN/gisp) #substitue proc declaration with PROC_START. We will handle it in a fragment handler
	{
		my ($prematch, $match, $postmatch) = (${^PREMATCH}, ${^MATCH}, ${^POSTMATCH});
		my $tmp_proc_nm = $1;
		$MR->log_msg("Found procedure declaration, plugging in PROC_START");
		$PROCEDURE_NAME = $tmp_proc_nm;
		$PROCEDURE_NAME =~ s/\[//g;
		$PROCEDURE_NAME =~ s/\]//g;
		$cont_str = "PROC_START $PROCEDURE_NAME\n$DELIM\n$postmatch";
	}

	$cont_str =~ s/SET\s+\@(\w+)\s*\=/$DELIM\nSELECT \@$1\=/gis;

	my @keywords = ("BULK INSERT", "DELETE", "INSERT", "UPDATE", "MERGE", "DECLARE", "BEGIN", "EXEC", "EXECUTE", "TRUNCATE");
	my $first_state = 1;
	
	
	$cont_str = replace_synapse_tables($cont_str);

	$cont_str =~ s/\bTHEN\b\s+\bINSERT\b/INSERT_IN_MERGE/gim;
	$cont_str =~ s/\bTHEN\b\s+\bUPDATE\b/UDPATE_IN_MERGE/gim;
	$cont_str =~ s/\bTHEN\b\s+\bDELETE\b/DELETE_IN_MERGE/gim;

	foreach my $kw (@keywords)
	{
		$cont_str =~ s/^\s*$kw/\n$DELIM\n$kw/gim;
	}
	$cont_str =~ s/(\bWITH\b\s+.*?\s+\bAS\b\s+\()/\n$DELIM\n$1/gim;

	# Correction to remove $DELIM in "INSERT INTO <tblname> $DELIM WITH"
	$cont_str =~ s/\b(insert\s+into\s+[\w.]+\s*)$DELIM(\s*WITH)/$1$2/gim;

	$cont_str =~ s/INSERT_IN_MERGE/ THEN\nINSERT /gim;
	$cont_str =~ s/UDPATE_IN_MERGE/ THEN\nUPDATE /gim;
	$cont_str =~ s/DELETE_IN_MERGE/ THEN\nDELETE /gim;
	#$cont_str =~ s/(declare\s.*?)\n(\bselect\b)/$1\n$DELIM\n$2/gis; #separate DECLARE from SELECT
	$cont_str =~ s/(\bselect\b\s+@\w+\s+=)/\n$DELIM\n$1/gis; #separate SELECT @variable

	$cont_str =~ s/$WITH_PREFIX//gim;

	# my @WITH_KW = qw(INSERT DELETE UPDATE);
	# foreach my $wkw (@WITH_KW)
	# {
	# 	$cont_str =~ s/$WITH_PREFIX_//gis;
	# }

	#special handling for SELECTs that were not handled earlier.  Need to separate them out
	my @sc_kw = ("GROUP BY", "ORDER BY"); #if any of these are followed by SELECT and it is on the same level (i.e. it is not a sub-query, then add the delimiter)
	my $matched_flag = 0;
	my $SELECT_SUBST = '__S3L3CT__'; #use this temporarily to avoid additional looping.  At the end of the loop substitute it to SELECT
	my $total_hits = 0;

	@ret = (@ret,split(/\n/, $cont_str));

	return @ret;
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
	$table_template =~ s/\%TABLE_NAME%/$table_name/gs;
	$ret =~ s/^\s*\;\s*$//gim;
	$ret = replace_params_as_spark($table_template.$ret, undef, 'query_'.$QUERY_INCREMENT);
	$ret = 'query_'.$QUERY_INCREMENT.' = spark.sql(' . $ret . ')';
	$QUERY_INCREMENT += 1;
	return code_indent($ret) . "\n";
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

sub convert_start_if
{
	my $ar = shift;
	my $sql = join("\n", @$ar);
	$MR->log_msg("convert_start_if:\n$sql");
	my $ret = $CONVERTER->convert_sql_fragment($MR->trim($sql));
	$ret =~ s/\@/$VARIABLE_PREFIX/gis;
	$ret =~ s/\s*;\s*$//gis;
	$ret =~ s/--.*//gim;
	$ret = $MR->trim($ret);
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
	# my $ret = $CONVERTER->convert_sql_fragment($MR->trim($sql));
	# $ret =~ s/\@/$VARIABLE_PREFIX/gis;
	# $ret =~ s/\s*;\s*$//gis;
	# $ret =~ s/--.*//gim;
	# $ret = $MR->trim($ret);
	# chomp($ret);
	$INDENT--;
	my $ret = code_indent("# END IF");
	#$ret =~ s/\s*$/\:/gis;
	return $ret;
}
