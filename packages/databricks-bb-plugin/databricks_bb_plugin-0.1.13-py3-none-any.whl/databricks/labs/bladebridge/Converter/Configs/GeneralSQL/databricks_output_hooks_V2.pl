use strict;
use Globals;
use Data::Dumper;
use Common::MiscRoutines;
use DWSLanguage;

no strict 'refs';

my $MR = new Common::MiscRoutines(MESSAGE_PREFIX => 'DBRKS_HOOKS');
my $LAN = new DWSLanguage();
my %CFG = (); #entries to be initialized
my $CFG_POINTER = undef;
my $CONVERTER = undef;
my $INDENT = 0; #keep track of indents
my $INDENT_ENTIRE_SCRIPT = 0;
my $FILENAME = '';
my %PRESCAN = ();
my $STOP_OUTPUT = 0;
my $SRC_TYPE ='';
my %USE_VARIABLE_QUOTE = ();

# notebook markdown specs
my $nb_COMMAND_sql     = '-- COMMAND ----------';
my $nb_COMMAND_python  = '# COMMAND ----------';

my %conv_cat = (); # Conversion catalog

my $sql_case_num = 0;   # Counter for hiding SQL CASE...END

my $global_indent_count = 0;

# For hiding anything (e.g. hiding comments so that we don't perform conversions on them) 
my $hide_num = 0;
my %hide_hash = ();

my $CATALOG = {};
my $IS_PYTHON_SCRIPT = 0;

my $PHYTON_SCOPE_LEVEL = 0;
my $BEGIN_LEVEL = 0;
my $sql_parser;
my $PREFIX_TAG = '';
my $CURSOR_SUFIX = '';
my $is_exception = 0;
my $IS_SCRIPT = '';
my $PROCESS_PACKAGE = undef;
my $SOURCE_FOLDER ='';
my @FINAL_SCRIPT ={};
my $FILE_EXTENSION ='';
my @pkg_files ={};
my $STRIP_EXECUTE ='';
my $TEMP_VIEW_CREATION_STATEMENT='';
my $USE_PREFIX='';
my $TARGET_CATALOG ='';
my @CATALOGS =();
my $IS_PROC;
my $ISDOLLAR;
my $INSERT_OVERWRITE; 
my $INCREMENTAL_WORKLOAD_HEADER='';
my $INCREMENTAL_WORKLOAD_FOOTER='';
my $TRANSACTION_CONTROL=0;
my $PYTHON_TEMPLATE='';
my $FUNCTION_TEMPLATE ='';
my $REMOVE_COMMIT_AND_ROLLBACK='';

sub databricks_prescan_wrapper
{
	my $filename = shift;
	$FILENAME = $filename; #save in a global var
	$MR->log_msg("******** databricks_prescan_wrapper $filename *********. CFG: $CFG_POINTER");

	my $ret = {PRESCAN_INFO => \%PRESCAN};

	return $ret;
}

sub init_databricks_hooks #register this function in the config file
{
	my $param = shift;
	%CFG = %{$param->{CONFIG}};
	$CFG_POINTER = $param->{CONFIG}; #give the ability to modify config incrementally
	$CONVERTER = $param->{CONVERTER};
	%USE_VARIABLE_QUOTE = ();

	foreach my $k (keys %$param)
	{
		$MR->log_msg("Init hooks params: $k: $param->{$k}");
	}
	$MR->log_msg("INIT_HOOKS Called. config:\n" . Dumper(\%CFG));
    
	#Reinitilize vars for when -d option is used:
	$INDENT = 0; #keep track of indents
	%PRESCAN = ();

	if($CFG_POINTER->{catalog_file_path})
	{
        fill_catalog_file($CFG_POINTER->{catalog_file_path});
    }
    
	$Globals::ENV{CONFIG} = $param->{CONFIG};
	$SRC_TYPE=$Globals::ENV{CONFIG}->{src_type}; 
    
    $PYTHON_TEMPLATE = $Globals::ENV{CONFIG}->{invoked_python_template_file}; 
	$FUNCTION_TEMPLATE = $Globals::ENV{CONFIG}->{invoked_python_function_template_file}; 

	$Globals::ENV{CONFIG}->{FILENAME} = $FILENAME;
	$PREFIX_TAG = $Globals::ENV{CONFIG}->{prefix_tag};
	$CURSOR_SUFIX = $Globals::ENV{CONFIG}->{cursor_sufix};
	$IS_SCRIPT = $Globals::ENV{CONFIG}->{is_script};
	$SOURCE_FOLDER = $Globals::ENV{CONFIG}->{source_folder};
	$PROCESS_PACKAGE = $Globals::ENV{CONFIG}->{process_package};
	$STRIP_EXECUTE = $Globals::ENV{CONFIG}->{strip_execute};
	$FILE_EXTENSION = $Globals::ENV{CONFIG}->{target_file_extension};
	$TEMP_VIEW_CREATION_STATEMENT = $Globals::ENV{CONFIG}->{temp_view_creation_statement};
	$USE_PREFIX = $Globals::ENV{CONFIG}->{use_prefix};
	$TARGET_CATALOG = $Globals::ENV{CONFIG}->{target_catalog};
	$INSERT_OVERWRITE = $Globals::ENV{CONFIG}->{insert_overwrite};
	$INCREMENTAL_WORKLOAD_FOOTER = $Globals::ENV{CONFIG}->{inceremental_footer};
	$INCREMENTAL_WORKLOAD_HEADER = $Globals::ENV{CONFIG}->{inceremental_header};
	$TRANSACTION_CONTROL = $Globals::ENV{CONFIG}->{dbt_transaction_control};
	@CATALOGS = $Globals::ENV{CONFIG}->{catalogs};
	$REMOVE_COMMIT_AND_ROLLBACK = $Globals::ENV{CONFIG}->{remove_commit_and_rollback};
	$sql_parser = new DBCatalog::SQLParser(CONFIG => $Globals::ENV{CONFIG}, DEBUG_FLAG => 0);
}

sub preprocess_for_databricks
{
	my $cont = shift; 


	my $modpack = eval('use DWSModulePacking; new DWSModulePacking(IGNORE_DB => 1);');
	$MR->log_msg("reload_modules Eval returned: $@") if $@;
	$modpack->init();
	if (defined $CFG_POINTER->{load_files}) #this is done so the global vars are being visible by load_files scripts
	{
		foreach my $f (@{$CFG_POINTER->{load_files}})
		{
			if (! -s $f)
			{
				$MR->log_error("load_files: File $f does not exist or have 0 size!");
				next;
			}
			my $fc = $f=~/dwsmod/?$modpack->decode_file($f):$MR->read_file_content($f);
			eval($fc);
			my $eval_ret = $@;
			$MR->log_error("load_files: Loading of File $f returned : $eval_ret") if $eval_ret;
		}
	}
	
	if (defined $CFG_POINTER->{source_prescan_routine})
	{
		my $prescan_hook = $CFG_POINTER->{source_prescan_routine};
		$MR->log_msg("Executing source specific hook $prescan_hook. MR: $MR");
		%PRESCAN = eval($prescan_hook . '($cont)');
		my $ret = $@;
		if ($ret)
		{
			$MR->log_error("************ EVAL ERROR prescan_hook: $ret ************");
			exit -1;
		}
	}
	
	if (defined $CFG_POINTER->{source_prescan_widgets})
	{
		my $prescan_hook = $CFG_POINTER->{source_prescan_widgets};
		$MR->log_msg("Executing source specific hook $prescan_hook. MR: $MR");
		%PRESCAN = eval($prescan_hook . '($cont)');
		my $ret = $@;
		if ($ret)
		{
			$MR->log_error("************ EVAL ERROR prescan_hook: $ret ************");
			exit -1;
		}
	}
	

	my $cont_string = join("\n", @$cont);
	$cont_string =~ s/^.*alter\s+session.*$//im;	
	$cont_string =~ s/\bEND\b\s*\$\$\s*\;/end;/gis;
	
	$ISDOLLAR =$Globals::ENV{PRESCAN}->{IS_DOLAR};
	$cont_string =~ s/\-\-(.*?)IF/--$1I_F/im;
	$cont_string =~ s/\-\-(.*?)loop/--$1lo_op/im;
	#$cont_string =~ s/\bINOUT\b/OUT/gis;
	#$cont_string =~ s/\bIN\b\s+\bOUT\b/OUT/gis;
	if ($INSERT_OVERWRITE)
	{
	
	 $cont_string =~ s/DELETE\s+FROM\s+(\w*\.*\w*\.*\w+)\s*\;\s+INSERT\s+INTO\s+\1/INSERT OVERWRITE $1/gis;
	 my @partitions = $cont_string =~ /(DELETE\s+FROM\s+(\w*\.*\w*\.*\w+).*?;\s+INSERT\s+INTO\s+\g{2}.*?\;)/gis;
	
     for my $prt(@partitions){
		 
		
		my $orig_prt = $prt; 
		if($prt =~ /DELETE\s+FROM\s+\w*\.*\w*\.*\w+\s+where\s+(\w*\.*\w+\s*\=\s*\'*\{*\w+\}*\'*).*?\;\s+INSERT\s+INTO.*\g{1}/gis)
		{
			 my $whr =$1;
		
			 $prt =~ s/DELETE\s+FROM\s+(\w*\.*\w*\.*\w+).*?\;\s+INSERT\s+INTO\s+\1/INSERT OVERWRITE $1 PARTITION($whr) /gis; 
			
			 $cont_string =~ s/\Q$orig_prt\E/$prt/gis;
		}

	 }	

	 
	}
	if($SRC_TYPE eq 'REDSHIFT')
	{   
	    $cont_string =~s/into\s+temp\s+table/into table /gis;
		
		
		$cont_string =~s/(\bselect\b\s+.*?)\bINTO\b\s+TABLE\b\s+(\w+\b)(.*?)\;/$2=spark.sql("""$1 $3""");/gis;

		# $cont_string =~s/(.*?\b(?<!\')SELECT\b.*?)(from.*?)(into\b.*?)where/$1 $3 $2 where/gis;  # regex too slow, use below instead
		$cont_string =~ s/(\bSELECT\b.*?)(\bFROM\b.*?)(\bINTO\b.*?)(\bWHERE\b)/$1$3$2$4/gis;
	
		my ($into_row_var) = $cont_string =~ /SELECT\s+INTO\s+(\w+)\b\s+\*/is;
		$cont_string =~ s/SELECT\s+\INTO\s+(\w+)\b\s*\*(.*?)\;\s+IF\s+NOT\s+FOUND/$1=spark.sql(f"""$2""");\nif($into_row_var.head()[0] is None): /gis;
		($into_row_var) = $cont_string =~ /SELECT.*?INTO\s+(\w+)\b\s+from/is;
		$cont_string =~ s/(SELECT\s+.*?\INTO\s+\w+\b\s*.*?\;)\s+IF\s+NOT\s+FOUND\s+then/$1\nif($into_row_var.head()[0] is None): /gis;
		$cont_string =~ s/($into_row_var\.)length/$1count()/gis;
		$cont_string =~ s/else\s+if(.*?)\bthen\b/EL_SEF($1):/gis;
		$cont_string =~ s/elsif(.*?)THEN/E_L_F$1:/gis;
        my($if_found) =$cont_string =~/(if\s+found\s+then\s+case.*?end\s+case\;)/gis;
		if($if_found){
		my $if_found2 =$if_found; 
		$if_found =~ s/if\s+found\s+then\b/if(dyn_df.count()>0)then;/gis;
		$if_found =~ s/case\s+when(.*?)then\b(.*?)\;/if($1)then\n$2;\nend if;/gis;
		$if_found =~ s/when(.*?)then(.*?)\;/elif($1)\nthen\n$2;\nend if;/gis;
		$if_found =~ s/end\s+case\s*\;//gis;
		$if_found =~ s/else/case_else/gis;
		#$if_found= $if_found."\nend if;";
		$cont_string =~ s/\Q$if_found2\E/$if_found/gis;

		}
	}
	if($cont_string =~/PROCEDURE\s+\"?\w+\"?\.?\"?\w*\"?\s*\((.*?)\)\s*(AS|IS)\b/gis)
	{
		my $prc_args=$1;
		
		my @out_args = $prc_args =~ /(\w+)\s+\bOUT\b/gis;
		my @out_args2 = $prc_args =~ /(\w+)\s+\bINOUT\b/gis;
		my @out_args3 = $prc_args =~ /(\w+)\s+\bIN\s+OUT\b/gis;
		push(@out_args, @out_args2);
		push(@out_args, @out_args3);
		my $return_output_params = '';
		for my $or  (@out_args)
		{
				if ($#out_args > -1)
				{
					$MR->log_msg("output_args $or ");
					$return_output_params = $return_output_params.",".$or; 		
				}
		}
		if($return_output_params ne '')
		{
				$return_output_params = "return(".$return_output_params.");";
				$return_output_params =~ s/\,\)/)/gis;
				$return_output_params =~ s/\(\,/(/gis;
			
				$cont_string = $cont_string."\n".$return_output_params;
		}
	    
	}
	if ($STRIP_EXECUTE){
	$cont_string =~ s/begin\s+EXECUTE\s+IMMEDIATE\s+[\'|\"](.*?)\'\s*\;\s+EXCEPTION.*?\bEND;/$1;/gis;	
	}
	
	$cont_string =~ s/(\w+)(\(\s*\+\s*\))/$1 $2/gis;
	$cont_string =~ s/\;\s*\"/"/gis;
	$cont_string =~ s/(^\s*\/\/.*?)\;/$1/gim;
	$cont_string =~ s/(\-\-.*?)\;/$1/gim;$MR->log_msg("if_found ".$cont_string);
	$cont_string =~ s/(\#.*?)\;/$1/gim;
	if(!$PROCESS_PACKAGE){
	$cont_string =~  s/\;\s+\/(?!\*|\/)/;\n/gis;$MR->log_msg("entering preprocess1:$cont_string");
	}
	my @cmnts = $cont_string =~/\/\*.*?\*\//gis;
	for my $cm(@cmnts){
		my $cm1=$cm;
		$cm =~ s/\;//gis;
		$cm =~ s/begin/b e g i n/gis;
		$cont_string =~ s/\Q$cm1\E/$cm/gis;
	}
	
	 
	#$cont_string=~s/\*\+/* _PLUS_/gis;
	
	if($SRC_TYPE eq 'SNOWFLAKE')
	{   
	
		$cont_string =~ s/as\s+\'(.*)\'s*\;/AS\n$1/gis;
		$cont_string =~ s/as\s+\$\$(.*)\$\$\s*\;/AS\n$1/gis;
		$cont_string =~ s/as(.*?)\$\$(.*)\$\$\s*\;/AS$1\n$2/gis;
		

	} 
	
	if ($CFG_POINTER->{add_create_for_not_precedure_scripts})
	{
        $cont_string =~ s/(function|procedure)/ $1/gis;
		$cont_string =~ s/(?<![CREATE|REPLACE])\s+(FUNCTION\s+(\"?\w+\"?\.?\"?\w*\"?)\s*\((.*?)\))/\nCREATE $1/gis;
		$cont_string =~ s/(?<![CREATE|REPLACE])\s+(PROCEDURE\s+(\"?\w+\"?\.?\"?\w*\"?)\s*\((.*?)\))/\nCREATE $1/gis;
		$cont_string =~ s/(?<![CREATE|REPLACE])\s+(PROCEDURE\s+(\"?\w+\"?\.?\"?\w*\"?)\s+(\bIS\b|\bAS\b))/\nCREATE $1/gis;
		$cont_string =~ s/CREATE\s+CREATE/CREATE /gis;
		$cont_string =~ s/REPLACE\s+CREATE/REPLACE /gis;
	}
	
	if(($cont_string =~ /CREATE\s+OR\s+REPLACE\s+PACKAGE\s+(\"*\w*\"*\.*\"*\w+\"*)/gis or $cont_string =~/CREATE\s+PACKAGE\s+(\"*\w*\"*\.*\"*\w+\"*)/gis) and $PROCESS_PACKAGE)
	{
				
				$cont_string = read_file($cont_string);
				
				@$cont = split(/\n/, $cont_string);
				@FINAL_SCRIPT =@$cont;
				#return @$cont;
			}
	
     if($SRC_TYPE eq 'SNOWFLAKE')
	{	
		
		my @switches = $cont_string =~/(switch\s*\(.*?\)\s*\{.*?\})/gis;
		if ($#switches > -1)
		{
			for my $sw (@switches)
			{
				my ($switch) = $sw =~/switch\s*\((.*?)\)\s*\{.*?\}/gis;
				my $sw2 =$sw;
				$sw =~ s/\}//gis;
				$sw =~ s/\{\s*CASE(.*?)\:/if $switch == $1\{/gis;
				$sw =~ s/CASE(.*?)\:/elsif $switch == $1\{/gis;
				$sw =~ s/\bdefault\s*\:/else\{/gis;
		 		#$sw =~ s/\;//gis;
				$sw =~ s/break\s*/\};/gis;
				$sw =~ s/switch\s*\(.*?\)//gis;
		  	    $cont_string =~ s/\Q$sw2\E/;$sw\n/gis;
			}
		}
		
		
		$cont_string =~ s/(\w+)\.next\(.*?\)\s*\;\s*\;*\s+var\s+(\w+)\s*\=\s*\1\.getColumnValue\(1\)\s*\;/$2 = $1.first()[0];/gis;
		$cont_string =~ s/(\w+)\.next\(.*?\)\s*\;\s*\;*\s+(\w+)\s*\=\s*\1\.getColumnValue\(1\)\s*\;/$2 = $1.first()[0];/gis;

		$cont_string =~ s/(LANGUAGE\s+JAVASCRIPT\s+AS\s*)\$\$(.*)\$\$/$1\n$2/gis;
		$cont_string =~ s/(\bCREATE\s+OR\b\s+REPLACE\s+PROCEDURE\s+.*?\bAS\b).*?(TRY|VAR)\b/$1;\n$2/gis;	
		$cont_string =~ s/(\bTRY\b\s*\{.*?)\bcatch\b/$1;catch/gis;
		$cont_string =~ s/(\bTRY\b\s*\{)/$1;/gis;
		$cont_string =~ s/(\}\s*)\belse\b/$1;else/gis;
		$cont_string =~ s/(\belse\b\s*{)/$1;/gis;
		$cont_string =~ s/(\belsif\b.*?{)/$1;/gis;
		$cont_string =~ s/(\bwhile\b.*?{)/$1;/gis;
		$cont_string =~ s/(\bcatch\b\s*\(\s*\w+\s*\)\s*{)/$1;/gis;
		$cont_string =~ s/(?<![\/\/|\w+])\s+\breturn\b/;return/gim;

		$cont_string =~ s/(\bif\b\s*\(.*?{)/;$1;/gis;
		$cont_string =~ s/(\bif\b\s*.*?{)/;$1;/gim;
		$cont_string =~ s/(\bvar\b)/;\n$1/gis;
		$cont_string =~ s/\;\s*\`/\`/gis;
		$cont_string =~ s/(\bsnowflake\.execute\b\s*\(\s*)\{(.*?)\}/$1_BEGIN_STMT_$2_END_STMT_/gis;
		$cont_string =~ s/(\bsnowflake\.createStatement\b\s*\(\s*)\{(.*?)\}/$1_BEGIN_STMT_$2_END_STMT_/gis;
		$cont_string =~ s/\}(?!\;|\')/\};/gis;
		$cont_string =~ s/(\w+\s+)(snowflake\.)/$1;$2/gis;
		$cont_string =~ s/_BEGIN_STMT_/{/gis;
		$cont_string =~ s/_END_STMT_/}/gis;
		$cont_string =~ s/^\s*rs.next\(\)/while(rs.next()){/gim;
	} 
	else
	{	
		$cont_string =~ s/RETURN\s+SYS_REFCURSOR/RETURN VARCHAR/gis;
		if($cont_string =~ /((PROCEDURE|FUNCTION).*?(\bAS\b|\bIS\b)).*?(\bBEGIN\b|\bTRY\b|\bCURSOR\b|\$\$)/gis and $IS_SCRIPT 		){
		#my ($cont_string2) = $cont_string =~ /([PROCEDURE|FUNCTION].*?)[\bAS\b|\bIS\b]?!\s+\w+\,).*?(BEGIN|TRY|CURSOR.*)/gis;
		 
		$cont_string =~ s/((PROCEDURE|FUNCTION).*?(\bAS\b|\bIS\b)).*?(\bBEGIN\b|\bTRY\b|\bCURSOR\b)/$1;\n$4/gis;
		$cont_string =~ s/\$\$//gis;
		$IS_PROC =1;
		}
	
	
	  
	}
	
	@$cont = split(/\n/, $cont_string);
	$cont = remove_empty_begin_end($cont);
	$cont_string = join("\n", @$cont);
	
	# adding create to function definions withou create keyword infront, packages may contain such cases. 

	
	my @crs_var = $cont_string =~/(cursor\s+\w+\s*is\s*.*?\;)/gis ;
	for my $cr (@crs_var)
	{
	if ($#crs_var > -1){
		my $cursor_body = $1;
		
		foreach my $arg_def (@{ $Globals::ENV{PRESCAN}->{PROC_ARGS} })
			{
				my $nrg =$arg_def->{NAME};
				if($nrg !~/cursor/is){
				$cursor_body =~s/(\b$nrg\b)/{$1}/gis;
				}
			}
		foreach my $var_def (@{ $Globals::ENV{PRESCAN}->{PROC_VARS} })
			{
				my $nrg =$var_def->{NAME};
				if($nrg !~/cursor/is){
				$cursor_body =~s/(\b$nrg\b)/{$1}/gis;
				}
			}	
		# $cont_string =~s/(?<!__CURSOR_START__)(cursor\s+\w+\s*is\s*.*?\;)/__CURSOR_START__$cursor_body/is;
		}
	}
	
	@crs_var = $cont_string =~/(cursor\s+\w+\s*\((.*?)\)\s*is\s*(.*?)\;)/gis ; 
	if ($#crs_var > -1)
	{
		for my $cr (@crs_var){
		if($cr =~/(cursor\s+\w+\s*\((.*?)\)\s*is\s*(.*?)\;)/gis)	
		{
		my $cursor_args = $2;
		my $cursor_body = $3;
		my @cursor_args_def = split(',',$cursor_args);
		foreach my $crs_arg (@cursor_args_def){
			$crs_arg = $MR->trim($crs_arg);
			if($crs_arg =~ /(\w+)\s+\w+/is)
			{
				my $split_arg =$1;

				$cursor_body =~s/($split_arg)/{$1}/gis;
				
			}
		}
		foreach my $arg_def (@{ $Globals::ENV{PRESCAN}->{PROC_ARGS} })
			{
				my $nrg =$arg_def->{NAME};
				if($nrg !~/cursor/is){
				$cursor_body =~s/(\b$nrg\b)/{$1}/gis;
				}
			}
		foreach my $var_def (@{ $Globals::ENV{PRESCAN}->{PROC_VARS} })
			{
				
				my $nrg =$var_def->{NAME};
				$MR->log_msg("cursor_args $nrg");
				if($nrg !~/cursor/is){
				$cursor_body =~s/(\b$nrg\b)/{$1}/gis;
				}
			}	
		
		
		# $cont_string =~s/(?<!__CURSOR_START__)cursor\s+(\w+)\s*\((.*?)\)\s*is\s*(.*?)\;/__CURSOR_START__$1 = """$cursor_body""";/is;
		}
	 }
	}
	
	$cont_string =~s/EXCEPTION\s+(\bWHEN\s+\bNO_DATA_FOUND|TOO_MANY_ROWS)/$1/gis;
	$cont_string =~s/(EXCEPTION\s+\when?)(\bEND\b)/$1_STOP_EXPTN_\;\nEND/gis; 
	
	$IS_PYTHON_SCRIPT = check_if_script_contains_python_elements($cont_string,1);
	
	foreach my $arg_def (@{ $Globals::ENV{PRESCAN}->{PROC_ARGS} })
	{
		my $proc_param = $arg_def->{NAME};
		if (!$IS_PYTHON_SCRIPT and !$IS_SCRIPT)
		{
			my $new_proc_param = '${'.$proc_param.'}';
			$cont_string =~ s/(?<!\{)$proc_param/$new_proc_param/gis; 
		}
	}
	foreach my $var_def (@{$Globals::ENV{PRESCAN}->{VARIABLES}})
	{
		my $proc_var = $var_def->{NAME};
		if (!$IS_PYTHON_SCRIPT and !$IS_SCRIPT)
		{
			my $new_proc_var = '${var.'.$proc_var.'}';
			$cont_string =~ s/$proc_var(?!\s*\:\=)/$new_proc_var/gis;
			$cont_string =~ s/$proc_var\s*\:\=/set var.$proc_var = /gis;
		}
	}
	
 		
	
	#$cont_string =~ s/^\s*\-\-(.*?$)/-- $1;/gim;
	my $is_python = check_if_script_contains_python_elements($cont_string);	
	if($is_python or $IS_SCRIPT)
	{
	
		$cont_string =~ s/DECLARE(?!\;)/DECLARE;/gis;
		#S$cont_string =~ s/(\bIF\b.*?)ELSE(?!\;)/$1ELSE;/gis;
		$MR->log_msg("exiting preprocess333:$cont_string preprocess333");
		
		$cont_string =~ s/SELECT\s+(\w+)(\(.*?\))\s+INTO/SELECT $1$2 $1_COL INTO/gis;
		$cont_string =~ s/(\bException\s+\w+\s+when\s+.*?\bTHEN\b(?!\;))/$1;/gis;
		$cont_string =~ s/\bIF\b(.*?)THEN\b(\s+)CONTINUE\s*\;/IF not $1 THEN $2break;/gis;
		$cont_string =~ s/(\bIF\b.*?THEN\b(?!\;))/$1;/gis;
		$cont_string =~ s/(\bException\s+when\s+.*?\bTHEN\b(?!\;))/$1;/gis;
		$cont_string =~ s/\bend\s+loop\b\s*\;/end_loop;/gis;
		$cont_string =~ s/\bend\s+loop\b\s*\w+\;/end_loop;/gis;
		$cont_string =~ s/\bend\s+if\b\s*\;/end_if;/gis;
		$cont_string =~ s/OPEN\s+\w+\s*(\(.*?\))\s*\;\s+\bLOOP\s+FETCH\s+(\w+)\s+INTO\s+(\w+)\s*\;/for $3 in $2.format$1 LOOP_START;/gis;	
		$cont_string =~ s/\bLOOP\s+FETCH\s+(\w+)\s+INTO\s+(\w+)\s*\;/for $2 in $1$CURSOR_SUFIX LOOP_START;/gis;
		$cont_string =~ s/(\bFOR\b\s+\w+\s+IN\s+\w+\s+LOOP\b)/$1_START;/gis;
		$cont_string =~ s/(\bWHILE\b.*?LOOP\b)(?!\;)\s*\n/$1_START;\n/gis;
	
		$cont_string =~ s/(\bFOR\b\s+\w+\s+IN\s+)(\d+)\s*\.\.\s*(\w+)\s+LOOP\b/$1 range($2,$3)LOOP_START;/gis;
		$cont_string =~ s/(\bFOR\b\s+\w+\s+IN\s+)(\d+)\s*\.\.\s*(\d+)\s+LOOP\b/$1 range($2,$3)LOOP_START;/gis;
		$cont_string =~ s/(LOOP\b)(?!\;)\s*\n/$1_START;\n/gis;
		$cont_string =~ s/(LOOP\b\s*\<\<\s*\w+\b\*>\>)(?!\;)\s*\n/$1_START;\n/gis;		
		$cont_string =~ s/(\bFOR\b\s+\w+\s+IN\s+)reverse\s*(\d+)\s*\.\.\s*(\w+)\s+LOOP\b/$1 reversed(range($2,$3))LOOP_START;/gis;
		$cont_string =~ s/(\bFOR\b\s+\w+\s+IN\s+)reverse\s*(\d+)\s*\.\.\s*(\d+)\s+LOOP\b/$1 reversed(range($2,$3))LOOP_START;/gis;
		$cont_string =~ s/\bFOR\b\s+(\w+)\s+IN\s+\((\s*SELECT.*?)\)\s*LOOP\b/$1_cursor = spark.sql("""$2""")\n;for $1 in $1_cursor LOOP_START;/gis;

		my @new_var = $cont_string =~/for\s+\w+\s+in\s+\w+\s+loop_start\s*\;.*?end_loop\;/gis ; 
		if ($#new_var > -1){
			for my $nr (@new_var){
			if ($nr =~/for\s+(\w+)\s+in\s+\w+\s+loop_start\s*\;(.*?)end_loop\;/gis){
			my $loop_row  = $1;
			my $loop_body = $2;
			my $loop_row2 = $loop_row.'["';
			#my $loop_body2 = $MR->deep_copy($loop_body);
			$loop_body =~ s/\b$loop_row\.(\w+)/$loop_row2$1"]/gis;
			$nr =~s/(for\s+\w+\s+in\s+\w+\s+loop_start\;)(.*?)end_loop\;/$1$loop_body end_loop;/gis;
			# $cont_string =~ s/(\n+\s*)(?<!__CURSOR_START__)(for\s+\w+\s+in\s+\w+\s+loop_start\s*\;)(.*?)end_loop\;/$1\n__CURSOR_START__$nr\n__CURSOR_START__;/is;
		
				}	
			}  
		} 
		
		@new_var = $cont_string =~/for\s+\w+\s+in\s+\w+\.format\(.*?\)\s+loop_start\s*\;.*?end_loop\;/gis ; 
		if ($#new_var > -1)
		{
			for my $nr (@new_var)
			{
				if ($nr =~/for\s+(\w+)\s+in\s+\w+\.format\(.*?\)\s+loop_start\s*\;(.*?)end_loop\;/gis)
				{
					my $loop_row  = $1;
					my $loop_body = $2;
					my $loop_row2 = $loop_row.'["';
					$loop_body =~ s/\b$loop_row\.(\w+)/$loop_row2$1"]/gis;
					$nr =~s/(for\s+\w+\s+in\s+\w+\.format\(.*?\)\s+loop_start\;)(.*?)end_loop\;/$1$loop_body end_loop;/gis;
					# $cont_string =~ s/(\n+\s*)(?<!__CURSOR_START__)(for\s+\w+\s+in\s+\w+\.format\(.*?\)\s+loop_start\s*\;)(.*?)end_loop\;/$1\n__CURSOR_START__$nr\n__CURSOR_START__;/is;
				}
			}  
		} 
		
		$cont_string =~ s/__CURSOR_START__//gis;
		
		$cont_string =~ s/(^s*\bwhile\b.*?\bloop\b)/$1;\n/gis;
		$cont_string =~ s/(^s*\bfor\b.*?\bloop\b)/$1;\n/gis;
		$cont_string =~ s/(^s*\bIF\b.*?\bTHEN\b)/$1;\n/gis;
		$cont_string =~ s/(^s*\bELSIF\b.*?\bTHEN\b)/$1;\n/gis;
		$cont_string =~ s/(\bBEGIN\b)/$1;\n/gis;
		$cont_string =~ s/^\s*end\s*;/end_empty;/gim;
		$cont_string =~ s/^\s*end\s*\$\$\s*;/end_empty;/gim;
	}
	if($ISDOLLAR==1)
	{
	$cont_string =~s/\$(\d+)/{ARG$1}/gis;
	}
	@$cont = split(/\n/, $cont_string);
	
	if ($CFG_POINTER->{tab_count_for_curly_bracket})
	{
        $cont = tab_counter_for_js($cont);
    }	
	# Read the conversion catalog file
	#my $conv_catalog = "$ENV{TEMP}/sqlconv_conversion_catalog.txt";
	#$conv_catalog = $CFG_POINTER->{conversion_catalog_file} if ($CFG_POINTER->{conversion_catalog_file});
	#my @conversion_catalog = $MR->read_file_content_as_array($conv_catalog);
	#foreach my $conv_cat_line (@conversion_catalog)
	#{
	#	# The ":::" separates key from value. It's up to the process that uses the information to extract
	#	# whatever is needed
	#	if ($conv_cat_line =~ m{(.*?):::(.*)}) {
	#		my ($conv_cat_key, $conv_cat_val) = ($1, $2);
	#		$conv_cat{$conv_cat_key} = $conv_cat_val;
	#	}
	#}

	
	case_to_if($cont);
  	
	return @$cont;
}

sub case_to_if
{
	my $cont = shift;
	my $cont_string = join("\n", @$cont);
    
	if ($cont_string =~ /\bINSERT\s+ALL\b/gis or $cont_string =~ /\bEXCEPTION\b/gis or $cont_string =~ /\bSELECT\b/gis or $cont_string =~ /\bFECTH\b/gis or  $cont_string =~/\bSWITCH\b/gis  )
	{$MR->log_msg("entering case_to_if $cont_string ");
		@$cont = split(/\n/, $cont_string);
	}
	else
	{
	# Disguise Stored Procedure CASE
	$cont_string =~ s{ ( ; | THEN )                                           # Anchor to ";" or "THEN"
		               ( ((\s*\-\-<<<c_o_m_m_e_n_t:\s+[0-9]+\s*)+)? | \s* )   # Then possible comments or space
		               CASE\b                                                 # Then CASE
	                 }
	                 {$1$2<:SP_C_A_S_E:>}xsig; 
	# Disguise SP END CASE
	$cont_string =~ s{\bEND\s+CASE\b}{<:SP_E_N_D_C_A_S_E:>}sig;

	# Hide Regular SQL CASE...END
	$cont_string =~ s{\bCASE\b.*?\bEND\b}{hide_sql_case($&)}esig;

	# Change "WHEN ... =" to "WHEN ... =="
	$cont_string =~ s{(\bWHEN\b.*?\bTHEN\b)}{handle_when_equal($1)}esig;

	# For Searched CASE, convert each first WHEN to an IF (SP_SEARCHED_I_F for now)
	$cont_string =~ s{<:SP_C_A_S_E:>
					  ( ((\s*\-\-<<<c_o_m_m_e_n_t:\s+[0-9]+\s*)+)? | \s* )
					  WHEN\b}
					 {SP_SEARCHED_C_A_S_E$1SP_SEARCHED_I_F}sxgi;

	# Hide the other Searched WHENs (determination of Searched WHEN, as opposed to Simple WHEN, is done in sub)
	$cont_string =~ s{\bWHEN\s+.*?\s+THEN\b}{hide_sp_searched_when($&)}esig;

	# Now convert remaining (i.e. Simple CASE) first WHENs to IF
	$cont_string =~ s{(<:SP_C_A_S_E:>\s*(.*?)\s*)WHEN\b}{$1IF $2 == }sig;

	my @case_subject = ();
	my @cont_array = split(/\n/, $cont_string);

	# Go line-by-line
	foreach my $cont_line (@cont_array)
	{
		$cont_line =~ s{\s+$}{};

		# Save CASE subjects. NOTE: Sometimes we save nothing (""), but we always have to save so
		# that when we hit an END CASE (SP_E_N_D_C_A_S_E) and "pop", we match the "push"
		if ($cont_line =~ m{(<:SP_C_A_S_E:>|SP_SEARCHED_C_A_S_E)\s*(.*)})   
		{
			push(@case_subject, $2);
		}

		# Avoid "WHEN [NOT] MATCHED" (happens in "MERGE INTO..." statement)
		next if ($cont_line =~ m{\bWHEN\s+(NOT\s+)?\bMATCHED\b}i);

		# Change Simple WHENs (Searched WHENs are hidden) to ELSEIFs
		#$cont_line =~ s{\bWHEN\b(.*?)\bTHEN\b}{ ELSEIF $case_subject[$#case_subject] == $1 THEN}sig;
		$cont_line =~ s{\bWHEN\b(?!\s+OTHERS)(.*?)\bTHEN\b}{ ELSEIF $case_subject[$#case_subject] == $1 THEN}sig;
		# If we hit and END CASE, then we need to pop the CASE subject off the stack
		if ($cont_line =~ m{<:SP_E_N_D_C_A_S_E:>\s*(.*)})
		{
			pop(@case_subject);
		}
	}

		$cont_string = join("\n", @cont_array);
		$cont_string =~ s{(<:SP_C_A_S_E:>\s*(.*?)\s*)IF\b}{IF}sig;
		$cont_string =~ s{<:SP_E_N_D_C_A_S_E:>(\s*;)?}{END IF;}sig;
		$cont_string =~ s{SP_SEARCHED_I_F}{IF}sig;
		$cont_string =~ s{SP_SEARCHED_W_H_E_N}{ELSEIF}sig;
		$cont_string =~ s{SP_SEARCHED_C_A_S_E}{}sig;
		$cont_string =~ s{<:SQL_C_A_S_E:([0-9]+)}{$Globals::ENV{PRESCAN}->{SQL_CASE}->{$1}}esig;
	    $cont_string =~ s/\bEND\s+IF\b/END_IF/gis;
		
		@$cont = split(/\n/, $cont_string);
	}
}

sub hide_sp_searched_when 
# Hide a "WHEN" in a Searched CASE in a Stored Procedure  
{
	my $when = shift;
	my $check_when = $when;
	$check_when =~ s{'.*?'}{}gs;
	if ($check_when =~ m{=|<|>})
	{
		$when =~ s{\bWHEN\b}{SP_SEARCHED_W_H_E_N}i;
	}
	return $when;
}

sub hide_sql_case
# Hide a regular SQL CASE
{
	my $case = shift;
	$sql_case_num++;
	$Globals::ENV{PRESCAN}->{SQL_CASE}->{$sql_case_num} = $case;
	return "\n<:SQL_C_A_S_E:" . $sql_case_num . "\n";
}

sub handle_when_equal
# Convert "=" to "==" in a Stored Procedure CASE "WHEN" clause
{
	my $when = shift;

	# Avoid "WHEN [NOT] MATCHED" (happens in "MERGE INTO..." statement)
	return $when if ($when =~ m{\bWHEN\s+(NOT\s+)?\bMATCHED\b}i);

	$when = hide($when, "'.*?'", '<:literals:>');
	$when =~ s{=}{==};
	$when = unhide($when, '<:literals:>');
	return $when;
}

sub databricks_default_handler
{
	my $ar = shift;
	return '' if $STOP_OUTPUT;
	my $script = join("\n", @$ar);
	$MR->log_msg("entering default_handler: $script");
	my $tab_tag = $CFG_POINTER->{tab_tag};
	$script = unpivot_to_stack($script);
	if ($script =~ /\bEXCEPTION\b/gis and $BEGIN_LEVEL > 1)
	{
		my $PHYTON_SCOPE_LEVEL_2 = $PHYTON_SCOPE_LEVEL-1;
		$tab_tag =~ s/\%count\%/$PHYTON_SCOPE_LEVEL_2/gis;
    }
	else
	{
		$tab_tag =~ s/\%count\%/$PHYTON_SCOPE_LEVEL/gis;
	}
		
	if ($BEGIN_LEVEL > 1)
	{
        $script =~ s/\bEXCEPTION\b/PYTHON_CATCH_$BEGIN_LEVEL/gis;
    }
    
	if ($PHYTON_SCOPE_LEVEL > 0)
	{
        $script = $PREFIX_TAG.$tab_tag.$script;
    }
	elsif($is_exception == 1 and $script ne '')
	{
		$script = $PREFIX_TAG.$tab_tag.$script;
	}
	
	
	my $is_python = check_if_script_contains_python_elements($script);
	if($is_python or $IS_SCRIPT)
	{
		#changing || to + in case its python, requires dealing with single quotes.
		
			if ( $SRC_TYPE eq 'ORACLE')
			{
				$script =~  s/\'\'\'\'\s*\|\|/"'"+/gis;
				$script =~  s/\|\|\s*\'\'\'\'/+"'"/gis;
				$script =~  s/(?<!\')\'(\s*)\|\|/'$1+/gis;
				$script =~  s/(?<!\')\'\'(?!\')(\s*\w+)/'$1/gis;
				$script =~  s/(\w+\s*)(?<!\')\'\'(?!\')/$1'/gis;
				$script =~  s/(\=\s*)(?<!\')\'\'\'(?!\')/='"""/gis;
				$script =~  s/(\s*\|\|)(?<!\')\'\'\'(?!\')/$1"""'/gis;
				$script =~  s/\"\"\"\s*\|\|/"""+/gis;
				$script =~  s/\|\|\s*\"\"\"/+"""/gis;
				$script =~  s/\;\s+\/(?!\*)\s+/;/gis;
			
			}
			if ($SRC_TYPE eq 'REDSHIFT' )
			{
			
				#$script =~  s/(?<!\')\'(?!\')/"""/gis;
				$script =~  s/(?<!\')\'\'(?!\')(\s*\w+)/'$1/gis;
				$script =~  s/(\w+\s*)(?<!\')\'\'(?!\')/$1'/gis;
				$script =~  s/(\=\s*)(?<!\')\'\'\'(?!\')/='"""/gis;
				$script =~  s/(\s*\|\|)(?<!\')\'\'\'(?!\')/$1"""'/gis;
				$script =~  s/\"\"\"\s*\|\|/"""+/gis;
				$script =~  s/\|\|\s*\"\"\"/+"""/gis;
				$script =~  s/\;\s+\/(?!\*)\s+/;/gis;
			
			}	
		
			if ($SRC_TYPE eq 'SNOWFLAKE')
			{
				$script =~  s/(?<!\")\"(?!\")/"""/gis;
				$script =~  s/(?!=)\s*\'\'(?!\;)/__TO_SINGLE__/gis;
				$script =~  s/\_\_TO_SINGLE\_\_/'/gis;
			}
		
		
		my @args = (@{ $Globals::ENV{PRESCAN}->{PROC_ARGS}},@{ $Globals::ENV{PRESCAN}->{FUNCTION_ARGS}});
		if ($script =~/\<python\>\<tab_count\:\d+\>\s*(insert|delete|update|merge|select|alter|raise)/gis or
			$script =~/\<python\>\s*(insert|delete|update|merge|select|alter)/gis)
		{

			foreach my $arg_def (@args)
			{
				my $proc_param = $arg_def->{NAME};
				my $new_proc_param = '{'.$proc_param.'}';
					
				$script =~ s/(?<!\{)\b$proc_param\b/$new_proc_param/gis;
				
			
			}			
			foreach my $var_def (@{$Globals::ENV{PRESCAN}->{VARIABLES}})
			{
			
				my $proc_var1 = $var_def->{NAME};
				my $new_proc_var1 = '{'.$proc_var1.'}';
				$script =~ s/(?<!\{)\b$proc_var1\b/$new_proc_var1/gis;
			}
		}
		elsif($script =~/\<python\>\<tab_count\:\d+\>.*?(\w+)\s*\(/gis )
		{
			foreach my $arg_def (@args)
			{
				my $proc_param = $arg_def->{NAME};
				my $new_proc_param = '{'.$proc_param.'}';
					
				#$script =~ s/\b$proc_param\b/$new_proc_param/gis;
				if ($script=~/\w+\s*\:\=(.*)/gis)
				{
					my $r = $1;
                    $r =~ s/\b$proc_param\b/$new_proc_param/gis;
					$script=~s/(\w+\s*\:\=)(.*)/$1$r/gis
                }				
			
			}
			
			foreach my $var_def (@{$Globals::ENV{PRESCAN}->{VARIABLES}})
			{
			
				my $proc_var1 = $var_def->{NAME};
				my $new_proc_var1 = '{'.$proc_var1.'}';
				if ($script=~/\w+\s*\:\=(.*)/gis)
				{
					my $r = $1;
                    $r =~ s/\b$proc_var1\b/$new_proc_var1/gis;
					$script=~s/(\w+\s*\:\=)(.*)/$1$r/gis
                }
			}			
		}		
	}

	if(!$IS_PYTHON_SCRIPT or $is_python or $IS_SCRIPT)
	{
		$script = wrap_args($script);
		if ($PHYTON_SCOPE_LEVEL==0 and ($is_python or  $IS_SCRIPT))
		{ 
			
			$script = $PREFIX_TAG.$tab_tag.$script;
		}	
			$MR->log_msg("exiting default_handler2: $script");
		my ($tabs) = $script=~/(\<python\>\<tab\_count\:\d+\>)/gis;
		if ($SRC_TYPE eq 'SNOWFLAKE')
			{
		$script=~s/(\n\s*\/\/)/\n$tabs\n$1/gis;
		$script=~s/(\/\/.*?$)/$1\n$tabs/gim;
			}
		else{
				$script=~s/(\n\s*\-\-)/\n$tabs\n$1/gis;
				$script=~s/(\-\-.*?$)/$1\n$tabs/gim;
			}
		return $sql_parser->convert_sql_fragment($script);
	}
	else
	{
		foreach my $arg_def (@{ $Globals::ENV{PRESCAN}->{PROC_ARGS} })
		{
			my $proc_param = $arg_def->{NAME};
			my $new_proc_param = '${'.$proc_param.'}';
			foreach my $item (@{$CFG_POINTER->{to_string_types}})
			{
				my $dt = $arg_def->{DATA_TYPE};
				
				if ($dt =~ /$item/gis)
				{
				
					$new_proc_param = "'$new_proc_param'";
                    last;
                }
			}			
			$script =~ s/\b$proc_param\b/$new_proc_param/gis;
		}
		foreach my $var_def (@{$Globals::ENV{PRESCAN}->{VARIABLES}})
		{
			my $proc_var = $var_def->{NAME};
			if ($script =~ /$proc_var\s*\:\=/)
			{
                $script =~ s/\b$proc_var\b\s*\:\=/set var.$proc_var = /gis;
            }
            else
			{
				my $new_proc_var = '${var.'.$proc_var.'}';
				$script =~ s/$proc_var/$new_proc_var/gis;
			}
		}
    }
	#$script = unpivot_to_stack($script);
	
	$script = $sql_parser->convert_sql_fragment($script);
	
	return $script;
}

sub adjust_statement
{
	my $sql = shift;

	# Add "ALTER TABLE <table name> ADD CONSTRAINT..." for various things:

	my $constraints = '';
	
	# CHECKs for BETWEENs
	foreach my $table_name (keys %{ $Globals::ENV{PRESCAN}->{BETWEEN} }) 
	{
		if ($sql =~ m{\sTABLE\s+$table_name})
		{
			foreach my $col_name (keys %{ $Globals::ENV{PRESCAN}->{BETWEEN}->{$table_name} })
			{
				$constraints .= "\nALTER TABLE $table_name ADD CONSTRAINT ${col_name}_RANGE CHECK " 
				             .  "(" . $col_name . " " . $Globals::ENV{PRESCAN}->{BETWEEN}->{$table_name}->{$col_name} . ");";
			}
		}
		$constraints .= "\n" if ($constraints);
	}

	# CHECKS for upper case
	foreach my $table_name (keys %{ $Globals::ENV{PRESCAN}->{UPPERCASE} }) 
	{
		if ($sql =~ m{\sTABLE\s+$table_name})
		{
			foreach my $col_name (keys %{ $Globals::ENV{PRESCAN}->{UPPERCASE}->{$table_name} })
			{
				$constraints .= "\nALTER TABLE $table_name ADD CONSTRAINT ${col_name}_uppercase CHECK " 
				             .  "(" . $col_name . " == upper(" . $col_name . "));";
			}
		}
		$constraints .= "\n" if ($constraints);
	}

	# Other CHECKs on columns
	foreach my $table_name (keys %{ $Globals::ENV{PRESCAN}->{COL_CHECKS} }) 
	{
		if ($sql =~ m{\sTABLE\s+$table_name})
		{
			foreach my $col_name (keys %{ $Globals::ENV{PRESCAN}->{COL_CHECKS}->{$table_name} })
			{
				$constraints .= "\nALTER TABLE $table_name ADD CONSTRAINT ${col_name}_checks CHECK (\n"
							 .  join(" AND\n",  @{ $Globals::ENV{PRESCAN}->{COL_CHECKS}->{$table_name}->{$col_name} }) . "\n);";
			}
		}
	}

	# Primary keys
	foreach my $table_name (keys %{ $Globals::ENV{PRESCAN}->{PRIMARY_KEYS} }) 
	{
		if ($sql =~ m{\sTABLE\s+$table_name})
		{
			foreach my $pk_name (keys %{ $Globals::ENV{PRESCAN}->{PRIMARY_KEYS}->{$table_name} })
			{
				$constraints .= "\nALTER TABLE $table_name ADD CONSTRAINT ${pk_name}_pk PRIMARY KEY \( $Globals::ENV{PRESCAN}->{PRIMARY_KEYS}->{$table_name}->{$pk_name}\);";
			}
		}
	}

	# Foreign keys
	foreach my $table_name (keys %{ $Globals::ENV{PRESCAN}->{FOREIGN_KEYS} }) 
	{
		if ($sql =~ m{\sTABLE\s+$table_name})
		{
			foreach my $fk_name (keys %{ $Globals::ENV{PRESCAN}->{FOREIGN_KEYS}->{$table_name} })
			{
				$constraints .= "\nALTER TABLE $table_name ADD CONSTRAINT ${fk_name} FOREIGN KEY \( $Globals::ENV{PRESCAN}->{FOREIGN_KEYS}->{$table_name}->{$fk_name} \);";
			}
		}
	}

	$sql .= $constraints;
	
	return $sql;
}

sub convert_dml
{
	my $ar = shift;
	my $sql = '';
	if (ref($ar) eq 'ARRAY') 
	{
		$sql = join("\n", @$ar);
	}
	else
	{
		$sql = $ar;
	}
	$MR->log_msg("convert_dml:\n$sql");
	my $ret = $CONVERTER->convert_sql_fragment($MR->trim($sql));
	$ret = $MR->trim($ret);
	return $ret . "\n";
}

#creating dynamic structure to store variables that need to be turned into widgets
sub databricks_sql_widget
{
	my $main = $CFG_POINTER->{VAR_DECL};
	my @final = ();
	foreach my $var ( keys %{$Globals::ENV{PRESCAN}->{VARIABLES}})
	{
		my $widget = $main; 
		$MR->log_msg("VAR widget: $widget // $var" . Dumper($var));
		$widget =~ s{%NAME%}{$Globals::ENV{PRESCAN}->{VARIABLES}->{$var}->{NAME}}ig;
		$widget =~ s{%DEFAULT%}{$Globals::ENV{PRESCAN}->{VARIABLES}->{$var}->{DEFAULT_VALUE}}gis;
		$widget =~ s/hiveconf\://gis;
		$MR->log_msg("VAR final widget: $widget");

		push(@final, $widget);
	}
	my $output = join("\n", @final);

	$ENV{WIDGET} = $output;

	return $output;
}

sub databricks_proc_arg_defs
# NOTE: We read the template file here, and create what will be the start of a Notebook.
# THEN we will update the template further in databricks_variable_declarations.
# So we MUST ALWAYS do this subroutine (in order to get the template file), but we
# may or may not have args to populate the template with here.
{
	my $ar = shift;   # This probably only contains "__PROC_DEF_PLACEHOLDER__;"
	if ($CFG_POINTER->{change_procedure_to_function}){
		my $nb_main = databricks_function_arg_defs($ar);
		
		return $nb_main;
	}
	
	#For simple SQL widgets directly in configuration file
	#if(!$CFG_POINTER->{invoked_notebook_template_file})
	#{
	#	$MR->log_msg("Starting SQL WIDGET");
	#	my $widgets = databricks_sql_widget();
	#	return $widgets;
	#}
	my $nb_main;
	if ($IS_PYTHON_SCRIPT or $IS_SCRIPT)
	{  
		$nb_main = $MR->read_file_content($MR->get_config_file_full_path($PYTHON_TEMPLATE));
		
		
    }
    else
	{
		$nb_main = $MR->read_file_content($CFG_POINTER->{invoked_sql_template_file});
	}
	
	# Get the template from the file. Everything beyond __END___ is ignored
	#my $nb_main = $MR->read_file_content($CFG_POINTER->{invoked_notebook_template_file});
	$nb_main =~ s{__END__.*}{}si;

	# Extract (with a substitution) each section into its own template
	my %templates = ();
	foreach my $nb_section ('ARG_DEF', 'ARG_GET', 'VAR_DECL', 'CONTINUE_HANDLER', 'ERROR_HANDLER', 'EXCEPT_BLOCK', 'RESULT_BLOCK') {
		$nb_main =~ s{(<\?$nb_section:> )  (.*?)  ( </$nb_section>       ) } {$1\n$3}xsig  && (        $templates{$nb_section} = $2);
		                                                                                             # $templ{section}{$nb_section}
	}

	# Result and except blocks have inner, reoccurring lines, so we need to extract those from their templates
	my %repeats = ();
	$templates{RESULT_BLOCK} =~ s{ ( <\?SET_RESULT_JSON:> )  (.*?)  ( </SET_RESULT_JSON> ) } {$1\n$3}xsig && ($repeats{SET_RESULT_VAR} = $2);
	$templates{EXCEPT_BLOCK} =~ s{ ( <\?ERROR_HANDLER_CALL:> )  (.*?)  ( </ERROR_HANDLER_CALL> ) } {$1\n$3}xsig && ($repeats{ERROR_HANDLER_CALL} = $2);

	# Remove trailing spaces from these templates
	$templates{ARG_DEF}  =~ s{\s+$}{};
	$templates{ARG_GET}  =~ s{\s+$}{};
	$templates{VAR_DECL} =~ s{\s+$}{};

	# For each Notebook arg, do a "definition" and a "get", if it is an "input" type,
	# and a "set result", if it is (possibly also) an "output" type 
	my %accum = ();  # For accumulating results of repeating thing
	my %final = ();  # For final things, ready to be put back into the main code

	foreach my $arg_def (@{ $Globals::ENV{PRESCAN}->{PROC_ARGS} })
	{
		$Globals::ENV{PRESCAN}->{ALL_VAR_NAMES}->{uc($MR->trim($arg_def->{NAME}))} = 1;

		if ($arg_def->{ARG_TYPE} eq 'IN' || $arg_def->{ARG_TYPE} eq 'INOUT' )
		{
			# Arg definition
			my $new_arg_def = $templates{ARG_DEF};  # $templates{ARG_DEF};
			$new_arg_def =~ s{%ARG_NAME%}{$arg_def->{NAME}}ig;
			$new_arg_def =~ s{%ARG_VALUE%}{$arg_def->{VALUE}}ig;
			$final{ARG_DEF} .= $new_arg_def;

			if($CFG_POINTER->{generate_widget_to_variable_assignments})
			{
				# Arg "get"
				my $new_arg_get = $templates{ARG_GET};
				$new_arg_get =~ s{%ARG_NAME%}{$arg_def->{NAME}}ig;
				my $data_type = lc($arg_def->{DATA_TYPE});
				$new_arg_get =~ s{%ARG_DATA_TYPE%}{$data_type}ig;
				$new_arg_get =~ s/string\(/str(/ig;
				$new_arg_get =~ s/integer\(/int(/ig;
				$final{ARG_GET} .= $new_arg_get;
			}
		}

		# Arg "set result" (so that it can be returned)
		if ($arg_def->{ARG_TYPE} eq 'OUT' || $arg_def->{ARG_TYPE} eq 'INOUT')
		{
			my $new_set_result_var = $repeats{SET_RESULT_VAR};
			$new_set_result_var =~ s{%VAR_NAME%}{$arg_def->{NAME}}ig;
			$accum{SET_RESULT_VAR} .= $new_set_result_var;
		}
	}

	if ($accum{SET_RESULT_VAR})
	{
		$accum{SET_RESULT_VAR} =~ s{,\s*$}{};  # Remove trailing comma
		$templates{RESULT_BLOCK} =~ s{ <\?SET_RESULT_JSON:>   .*? </SET_RESULT_JSON>  }{$accum{SET_RESULT_VAR}}xsi;
		$final{RESULT_BLOCK} = $templates{RESULT_BLOCK};
	}
	else
	{
		$final{RESULT_BLOCK} = '';
	}

	# Gather each variable into a "final" list
	foreach my $var_def (@{$Globals::ENV{PRESCAN}->{VARIABLES}})
	{   
		$Globals::ENV{PRESCAN}->{ALL_VAR_NAMES}->{uc($MR->trim($var_def->{NAME}))} = 1;

		my $new_var_decl = $templates{VAR_DECL};
		$new_var_decl =~ s{%VAR_NAME%}{$var_def->{NAME}}ig;

		my $data_type   = $var_def->{DATA_TYPE};
		my $default_val = $var_def->{DEFAULT_VALUE};

		# Remove surrounding quotes or double-quotes
		$default_val =~ s{^ (['"]) (.*) \1 }{$2}xs;

		# Set Databricks default value according to data type and whether or not a default value is present:
		#                                                |  Default Value 
		#     Data Type                                  |    Present /           | Databricks Default value
		#                      (DEC=decimal)             |  Not Present?          |
		#     -----------------------------------------   ------------------------  ------------------------------------------------------
		if    ($data_type =~ m{^DEC}                   &&    $default_val )      {  $default_val = 'decimal.Decimal(' . $default_val . ')'}
		elsif ($data_type =~ m{^DEC}                   &&  ! $default_val )      {  $default_val = 'decimal.Decimal(0)'}
		elsif (   $MR->is_datatype_number($data_type)  &&    $default_val )      {}   # No action ($default_val stays as-is)
		elsif (   $MR->is_datatype_number($data_type)  &&  ! $default_val )      {  $default_val = '0'   }
		elsif ( ! $MR->is_datatype_number($data_type)  &&    $default_val )      {  $default_val = '"' . $default_val . '"'   } 
		elsif ( ! $MR->is_datatype_number($data_type)  &&  ! $default_val )      {  $default_val = '""'   } 

		# If default value contains line feed(s), then we need to triple-double-quote it
		$default_val = '""' . $default_val . '""' if ($default_val =~ m{\n});

        if($default_val =~ /(select|insert|Update|delete|alter|drop|merge)/is)
		{
			my $spark_with_head = $CFG_POINTER->{commands}->{SPARK_WITH_HEAD};
			$spark_with_head =~ s/\%VALUE\%/$default_val/gis;
			#$default_val = "spark.sql(f".$default_val.").first()[0];";
			$default_val = wrap_args($spark_with_head);
		}
		
		$new_var_decl =~ s{%VAR_DEFAULT_VALUE%}{$default_val}ig;
		$final{VAR_DECL} .= $new_var_decl;
	}



	foreach my $var_def (@{$Globals::ENV{PRESCAN}->{PROC_ARGS}})
	{   
		
		if($var_def->{ARG_TYPE} eq 'OUT')
		{



			$Globals::ENV{PRESCAN}->{ALL_ARG_NAMES}->{uc($MR->trim($var_def->{NAME}))} = 1;

			my $new_var_decl = $templates{VAR_DECL};
			$new_var_decl =~ s{%VAR_NAME%}{$var_def->{NAME}}ig;

			my $data_type   = $var_def->{DATA_TYPE};
			my $default_val = $var_def->{DEFAULT_VALUE};

			# Remove surrounding quotes or double-quotes
			$default_val =~ s{^ (['"]) (.*) \1 }{$2}xs;

			# Set Databricks default value according to data type and whether or not a default value is present:
			#                                                |  Default Value 
			#     Data Type                                  |    Present /           | Databricks Default value
			#                      (DEC=decimal)             |  Not Present?          |
			#     -----------------------------------------   ------------------------  ------------------------------------------------------
			if    ($data_type =~ m{^DEC}                   &&    $default_val )      {  $default_val = 'decimal.Decimal(' . $default_val . ')'}
			elsif ($data_type =~ m{^DEC}                   &&  ! $default_val )      {  $default_val = 'decimal.Decimal(0)'}
			elsif (   $MR->is_datatype_number($data_type)  &&    $default_val )      {}   # No action ($default_val stays as-is)
			elsif (   $MR->is_datatype_number($data_type)  &&  ! $default_val )      {  $default_val = '0'   }
			elsif ( ! $MR->is_datatype_number($data_type)  &&    $default_val )      {  $default_val = '"' . $default_val . '"'   } 
			elsif ( ! $MR->is_datatype_number($data_type)  &&  ! $default_val )      {  $default_val = '""'   } 

			# If default value contains line feed(s), then we need to triple-double-quote it
			$default_val = '""' . $default_val . '""' if ($default_val =~ m{\n});

	        if($default_val =~ /(select|insert|Update|delete|alter|drop|merge)/is)
			{
				my $spark_with_head = $CFG_POINTER->{commands}->{SPARK_WITH_HEAD};
				$spark_with_head =~ s/\%VALUE\%/$default_val/gis;
				#$default_val = "spark.sql(f".$default_val.").first()[0];";
				$default_val = wrap_args($spark_with_head);
			}
			
			$new_var_decl =~ s{%VAR_DEFAULT_VALUE%}{$default_val}ig;
			$final{VAR_DECL} .= $new_var_decl;
		}
	}
	# Continue handler
	foreach my $continue_handler (@{$Globals::ENV{PRESCAN}->{DECLARE_CONTINUE_HANDLER}})
	{
		my $new_continue_handler = $templates{CONTINUE_HANDLER};
		$continue_handler =~ s{^}{# }mg;  # Comment out the entire thing
		$new_continue_handler =~ s{%DECLARE_CONTINUE%}{$continue_handler};
		$final{CONTINUE_HANDLER} .= $new_continue_handler;
	}

	# Error handler and "except:"
	my $error_handler_num = 0;
	foreach my $exit_handler (@{$Globals::ENV{PRESCAN}->{DECLARE_EXIT_HANDLER}})
	{
		my $new_error_handler = $templates{ERROR_HANDLER};
		my $new_error_handler_call = $repeats{ERROR_HANDLER_CALL};
		$error_handler_num++;
		$exit_handler->{CONDITION} =~ s{\n}{ }g; # Want this to fit on a single comment line
		$new_error_handler =~ s{%ERROR_HANDLER_NUM%}{$error_handler_num};
		$new_error_handler_call =~ s{%ERROR_HANDLER_NUM%}{$error_handler_num};
		$new_error_handler =~ s{%ERROR_CONDITION%}{$exit_handler->{CONDITION}};

		# $new_error_handler =~ s{%ERROR_ACTION%}{$exit_handler->{ACTION}};
		my $error_handler_stmts = '';

		# Insert a ";" after a BEGIN so that it goes through the below split separately
		$exit_handler->{ACTION} =~ s{^.*?\bBEGIN\s}{$&;}si;

		# We might have a mixture of SQL statements and SET statements, so they need to
		# be split out and the SQL statements need to be wrapped in "spark.sql..."
		foreach my $stmt (split (/;/, $exit_handler->{ACTION}))
		{
			if ($stmt =~ m{^.*?\bBEGIN\s}si)       # Comment out BEGIN
			{
				my $begin = $&;
				$begin =~ s{^}{# }mg;
				$error_handler_stmts .= "$begin\n";
				next;
			}
			if ($stmt =~ m{^\s*SET\s}si) 
			{
				$stmt =~ s{^\s+}{};

				# Convert: SET X = '...\n...' to: X = """...\n...""", otherwise just remove the "SET"
				$stmt =~ s{\bSET\s+(\w+\s*\=\s*)((['"])(.*?\n.*?)\s*\3)}{$1"""$4"""}si;
				$stmt =~ s{\bSET\s+(\w+\s*\=)}{$1}si;

				$error_handler_stmts .= "  $stmt\n";
				next;
			}
			if ($stmt =~ m{^\s*END\b}si)          # Comment out END
			{
				my $end = $&;
				$end =~ s{^}{# }mg;
				$error_handler_stmts .= "$end\n";
				next;
			}
			# Otherwise (SQL)
			$error_handler_stmts .= '  spark.sql("""' . "\n"
			                     .  "      $stmt\n"
			                     .  '  """.format(' . "\n"
			                     .  '        # SQLSTATE=SQLSTATE' . "\n"
			                     .  '  )).show(truncate = False)' . "\n";
		}
		$error_handler_stmts =~ s{\n\n}{\n}g;
		$new_error_handler =~ s{%ERROR_ACTION%}{$error_handler_stmts};

		$final{ERROR_HANDLER} .= $new_error_handler;
		$accum{ERROR_HANDLER_CALL} .= $new_error_handler_call;
	}

	if ($error_handler_num)
	{
		$nb_main =~ s{%TRY%}{# COMMAND ----------\ntry:\n--<indent++>};
		$templates{EXCEPT_BLOCK} =~ s{<\?ERROR_HANDLER_CALL:> .*? <?ERROR_HANDLER_CALL>}{$accum{ERROR_HANDLER_CALL}}xsi;
		$final{EXCEPT_BLOCK} = $templates{EXCEPT_BLOCK};
	}
	else
	{
		$nb_main =~ s{%TRY%}{};
		$final{EXCEPT_BLOCK} = '';
	}

	# Put the various final sections back into the main template 
	foreach my $nb_section ('ARG_DEF', 'ARG_GET', 'VAR_DECL', 'CONTINUE_HANDLER', 'ERROR_HANDLER', 'EXCEPT_BLOCK', 'RESULT_BLOCK')
	{
		$nb_main =~ s{ <\?$nb_section:>   .*?  </$nb_section>  } {$final{$nb_section}}xsi;
	}

	# For the bits below %BODY%, we need to put them aside so that the rest of the Notebook can be inserted
	# (elsewhere), so we put these bits into an "and bit"
	$nb_main =~ s{%BODY% (.*) } {}xsi && push (@{ $Globals::ENV{PRESCAN}->{NOTEBOOK_END} }, $1);
	$nb_main =~ s/varchar\( dbutils/str( dbutils/gis;
	$nb_main =~ s/number\( dbutils/int( dbutils/gis;
	$nb_main =~ s/\w*char.*?\(\s*dbutils/str( dbutils/gis;
    $nb_main =~ s/number.*\(\s*dbutils/int( dbutils/gis;
    $nb_main =~ s/integerw+\(\s*dbutils/int( dbutils/gis;
	$nb_main =~ s/bigint+\(\s*dbutils/int( dbutils/gis;
	$nb_main =~ s/long+\(\s*dbutils/int( dbutils/gis;
    $nb_main =~ s/(\s*\w+\s*\=\s*)time.*?(\(\s*dbutils.*?$)/\n# FIXME next line databricks.migration.task need date cast\n$1str$2/gis;
    $nb_main =~ s/(\s*\w+\s*\=\s*)date.*?(\(\s*dbutils.*?$)/\n# FIXME next line databricks.migration.task need date cast\n$1str$2/gis;
    $nb_main =~ s/(\s*\w+\s*\=\s*)\w*lob.*?(\(\s*dbutils.*?$)/\n# FIXME next line databricks.migration.task need *lob cast\n$1str$2/gis;
    $nb_main =~ s/(\s*\w+\s*\=\s*)\w*\s*raw.*?(\(\s*dbutils.*?$)/\n# FIXME next line databricks.migration.task need *raw cast\n$1str$2/gis;
    $nb_main =~ s/(\s*\w+\s*\=\s*)Bfile.*?(\(\s*dbutils.*?$)/\n# FIXME next line databricks.migration.task need date bfile\n$1 str$2/gis;


	$nb_main =~ s/\n+/\n/g; 

	return $nb_main;
}

sub databricks_function_arg_defs
{
	my $ar = shift;

	my $nb_main = $MR->read_file_content($MR->get_config_file_full_path($FUNCTION_TEMPLATE));
	
	# Get the template from the file. Everything beyond __END___ is ignored
	$nb_main =~ s{__END__.*}{}si;

	# Extract (with a substitution) each section into its own template
	my %templates = ();
	foreach my $nb_section ('FUNCTION_DECL','VAR_DECL', 'CONTINUE_HANDLER', 'ERROR_HANDLER', 'EXCEPT_BLOCK', 'RESULT_BLOCK')
	{
		$nb_main =~ s{(<\?$nb_section:> )  (.*?)  ( </$nb_section>       ) } {$1\n$3}xsig  && (        $templates{$nb_section} = $2);
	}

	# Result and except blocks have inner, reoccurring lines, so we need to extract those from their templates
	my %repeats = ();
	$templates{RESULT_BLOCK} =~ s{ ( <\?SET_RESULT_JSON:> )  (.*?)  ( </SET_RESULT_JSON> ) } {$1\n$3}xsig && ($repeats{SET_RESULT_VAR} = $2);
	$templates{EXCEPT_BLOCK} =~ s{ ( <\?ERROR_HANDLER_CALL:> )  (.*?)  ( </ERROR_HANDLER_CALL> ) } {$1\n$3}xsig && ($repeats{ERROR_HANDLER_CALL} = $2);

	# Remove trailing spaces from these templates
	#$templates{ARG_DEF}  =~ s{\s+$}{};
	#$templates{ARG_GET}  =~ s{\s+$}{};
	$templates{VAR_DECL} =~ s{\s+$}{};

	# For each Notebook arg, do a "definition" and a "get", if it is an "input" type,
	# and a "set result", if it is (possibly also) an "output" type 
	my %accum = ();  # For accumulating results of repeating thing
	my %final = ();  # For final things, ready to be put back into the main code
	my $arg_def_str='';
	foreach my $arg_def (@{ $Globals::ENV{PRESCAN}->{FUNCTION_ARGS} })
	{
		$Globals::ENV{PRESCAN}->{ALL_VAR_NAMES}->{uc($MR->trim($arg_def->{NAME}))} = 1;

		if ($arg_def_str ne '')
		{
            $arg_def_str .= ',';
        }
        
		$arg_def_str .= $arg_def->{NAME};
		if ($arg_def->{VALUE})
		{
            $arg_def_str .= " = $arg_def->{VALUE}";
        }
        
		#if ($arg_def->{ARG_TYPE} eq 'IN' || $arg_def->{ARG_TYPE} eq 'INOUT')
		#{
		# Arg definition
		#my $new_arg_def = $templates{ARG_DEF};  # $templates{ARG_DEF};
		#$new_arg_def =~ s{%ARG_NAME%}{$arg_def->{NAME}}ig;
		#$new_arg_def =~ s{%ARG_VALUE%}{$arg_def->{VALUE}}ig;
		#
		#$final{ARG_DEF} .= $new_arg_def;

		#}

		## Arg "set result" (so that it can be returned)
		#if ($arg_def->{ARG_TYPE} eq 'OUT' || $arg_def->{ARG_TYPE} eq 'INOUT')
		#{
		#	my $new_set_result_var = $repeats{SET_RESULT_VAR};
		#	$new_set_result_var =~ s{%VAR_NAME%}{$arg_def->{NAME}}ig;
		#	$accum{SET_RESULT_VAR} .= $new_set_result_var;
		#}
	}
	my $func_declaration = $templates{FUNCTION_DECL};
	$func_declaration =~ s/\%FUNCTION_NAME\%/$Globals::ENV{PRESCAN}->{FUNCTION_NAME}/gis;
	$func_declaration =~ s/\%FUNCTION_ARGS\%/$arg_def_str/gis;
	$final{FUNCTION_DECL} = $func_declaration;
	
	if ($accum{SET_RESULT_VAR})
	{
		$accum{SET_RESULT_VAR} =~ s{,\s*$}{};  # Remove trailing comma
		$templates{RESULT_BLOCK} =~ s{ <\?SET_RESULT_JSON:>   .*? </SET_RESULT_JSON>  }{$accum{SET_RESULT_VAR}}xsi;
		$final{RESULT_BLOCK} = $templates{RESULT_BLOCK};
	}
	else
	{
		$final{RESULT_BLOCK} = '';
	}

	# Gather each variable into a "final" list
	foreach my $var_def (@{$Globals::ENV{PRESCAN}->{VARIABLES}})
	{
		$Globals::ENV{PRESCAN}->{ALL_VAR_NAMES}->{uc($MR->trim($var_def->{NAME}))} = 1;

		my $new_var_decl = $templates{VAR_DECL};
		$new_var_decl =~ s{%VAR_NAME%}{$var_def->{NAME}}ig;

		my $data_type   = $var_def->{DATA_TYPE};
		my $default_val = $var_def->{DEFAULT_VALUE};

		# Remove surrounding quotes or double-quotes
		$default_val =~ s{^ (['"]) (.*) \1 }{$2}xs;

		# Set Databricks default value according to data type and whether or not a default value is present:
		#                                                |  Default Value 
		#     Data Type                                  |    Present /           | Databricks Default value
		#                      (DEC=decimal)             |  Not Present?          |
		#     -----------------------------------------   ------------------------  ------------------------------------------------------
		if    ($data_type =~ m{^DEC}                   &&    $default_val )      {  $default_val = 'decimal.Decimal(' . $default_val . ')'}
		elsif ($data_type =~ m{^DEC}                   &&  ! $default_val )      {  $default_val = 'decimal.Decimal(0)'}
		elsif (   $MR->is_datatype_number($data_type)  &&    $default_val )      {}   # No action ($default_val stays as-is)
		elsif (   $MR->is_datatype_number($data_type)  &&  ! $default_val )      {  $default_val = '0'   }
		elsif ( ! $MR->is_datatype_number($data_type)  &&    $default_val )      {  $default_val = '"' . $default_val . '"'   } 
		elsif ( ! $MR->is_datatype_number($data_type)  &&  ! $default_val )      {  $default_val = '""'   } 

		# If default value contains line feed(s), then we need to triple-double-quote it
		$default_val = '""' . $default_val . '""' if ($default_val =~ m{\n});

		if($default_val =~ /(merge|select|insert|Update|delete|alter|drop|merge)/is)
		{
			my $spark_with_head = $CFG_POINTER->{commands}->{SPARK_WITH_HEAD};
			$spark_with_head =~ s/\%VALUE\%/$default_val/gis;
			#$default_val = "spark.sql(f".$default_val.").fisrt()[0];";
			$default_val = wrap_args($spark_with_head);
		}

		$new_var_decl =~ s{%VAR_DEFAULT_VALUE%}{$default_val}ig;
		$final{VAR_DECL} .= $new_var_decl;
	}

	# Continue handler
	foreach my $continue_handler (@{$Globals::ENV{PRESCAN}->{DECLARE_CONTINUE_HANDLER}})
	{
		my $new_continue_handler = $templates{CONTINUE_HANDLER};
		$continue_handler =~ s{^}{# }mg;  # Comment out the entire thing
		$new_continue_handler =~ s{%DECLARE_CONTINUE%}{$continue_handler};
		$final{CONTINUE_HANDLER} .= $new_continue_handler;
	}

	# Error handler and "except:"
	my $error_handler_num = 0;
	foreach my $exit_handler (@{$Globals::ENV{PRESCAN}->{DECLARE_EXIT_HANDLER}})
	{
		my $new_error_handler = $templates{ERROR_HANDLER};
		my $new_error_handler_call = $repeats{ERROR_HANDLER_CALL};
		$error_handler_num++;
		$exit_handler->{CONDITION} =~ s{\n}{ }g; # Want this to fit on a single comment line
		$new_error_handler =~ s{%ERROR_HANDLER_NUM%}{$error_handler_num};
		$new_error_handler_call =~ s{%ERROR_HANDLER_NUM%}{$error_handler_num};
		$new_error_handler =~ s{%ERROR_CONDITION%}{$exit_handler->{CONDITION}};

		# $new_error_handler =~ s{%ERROR_ACTION%}{$exit_handler->{ACTION}};
		my $error_handler_stmts = '';

		# Insert a ";" after a BEGIN so that it goes through the below split separately
		$exit_handler->{ACTION} =~ s{^.*?\bBEGIN\s}{$&;}si;

		# We might have a mixture of SQL statements and SET statements, so they need to
		# be split out and the SQL statements need to be wrapped in "spark.sql..."
		foreach my $stmt (split (/;/, $exit_handler->{ACTION}))
		{
			if ($stmt =~ m{^.*?\bBEGIN\s}si)       # Comment out BEGIN
			{
				my $begin = $&;
				$begin =~ s{^}{# }mg;
				$error_handler_stmts .= "$begin\n";
				next;
			}
			if ($stmt =~ m{^\s*SET\s}si) 
			{
				$stmt =~ s{^\s+}{};

				# Convert: SET X = '...\n...' to: X = """...\n...""", otherwise just remove the "SET"
				$stmt =~ s{\bSET\s+(\w+\s*\=\s*)((['"])(.*?\n.*?)\s*\3)}{$1"""$4"""}si;
				$stmt =~ s{\bSET\s+(\w+\s*\=)}{$1}si;

				$error_handler_stmts .= "  $stmt\n";
				next;
			}
			if ($stmt =~ m{^\s*END\b}si)          # Comment out END
			{
				my $end = $&;
				$end =~ s{^}{# }mg;
				$error_handler_stmts .= "$end\n";
				next;
			}
			# Otherwise (SQL)
			$error_handler_stmts .= '  spark.sql("""' . "\n"
			                     .  "      $stmt\n"
			                     .  '  """.format(' . "\n"
			                     .  '        # SQLSTATE=SQLSTATE' . "\n"
			                     .  '  )).show(truncate = False)' . "\n";
		}
		$error_handler_stmts =~ s{\n\n}{\n}g;
		$new_error_handler =~ s{%ERROR_ACTION%}{$error_handler_stmts};

		$final{ERROR_HANDLER} .= $new_error_handler;
		$accum{ERROR_HANDLER_CALL} .= $new_error_handler_call;
	}

	if ($error_handler_num)
	{
		$nb_main =~ s{%TRY%}{# COMMAND ----------\ntry:\n--<indent++>};
		$templates{EXCEPT_BLOCK} =~ s{<\?ERROR_HANDLER_CALL:> .*? <?ERROR_HANDLER_CALL>}{$accum{ERROR_HANDLER_CALL}}xsi;
		$final{EXCEPT_BLOCK} = $templates{EXCEPT_BLOCK};
	}
	else
	{
		$nb_main =~ s{%TRY%}{};
		$final{EXCEPT_BLOCK} = '';
	}

	# Put the various final sections back into the main template 
	foreach my $nb_section ('FUNCTION_DECL','VAR_DECL', 'CONTINUE_HANDLER', 'ERROR_HANDLER', 'EXCEPT_BLOCK', 'RESULT_BLOCK')
	{
		$nb_main =~ s{ <\?$nb_section:>   .*?  </$nb_section>  } {$final{$nb_section}}xsi;
	}

	# For the bits below %BODY%, we need to put them aside so that the rest of the Notebook can be inserted
	# (elsewhere), so we put these bits into an "and bit"
	$nb_main =~ s{%BODY% (.*) } {}xsi && push (@{ $Globals::ENV{PRESCAN}->{NOTEBOOK_END} }, $1);
	$nb_main =~ s/\n+/\n/g;
	#$PHYTON_SCOPE_LEVEL += 1;
    $PHYTON_SCOPE_LEVEL += 1;
	$BEGIN_LEVEL += 1;
	$nb_main = $sql_parser->convert_sql_fragment($nb_main);
	
	
	return $nb_main;
}

sub databricks_select_into
{
	my $cont = shift;

	# Prevents false matches	
	return $cont if ( ! $Globals::ENV{PRESCAN}->{SELECT_INTO});

	my $select_into = shift @{$Globals::ENV{PRESCAN}->{SELECT_INTO}};

	#--- Get the INTO cols (Needed for "col1, col2, = spark...")
	my $into_cols = '';
	my $into = $select_into->{INTO};
	$into =~ s{^\s*INTO\s+}{};
	while ($into =~ m{(\w+)}g) {
		my $into_col = $1;
		$into_cols .= "$into_col, ";
		$Globals::ENV{PRESCAN}->{ALL_VAR_NAMES}->{uc($MR->trim($into_col))} = 1;
	}

	#--- For the WHERE, conevrt :var to {var} (needed for "WHERE...")
	my $from_where = $select_into->{WHERE};
	$from_where =~ s{:(\w+)}{\{$1\}}g;

	#--- Also need WHERE cols with just plain names for "format(column=var)..."
	my ($format_cols) = $select_into->{WHERE} =~ m{^\s*WHERE\s+(.*)}si;
	$format_cols =~ s{:}{}g;
		
	my $output = $into_cols . '= spark.sql("""' . "\n" .
                $select_into->{SELECT} . "\n" .
                $select_into->{FROM} . "\n" . 
                $from_where  . "\n" .
                '""".format(' . "\n" .
                $format_cols . "\n" .
             ')).first().asDict().values()' . "\n";

    return "<:nowrap:>$output";
}

sub databricks_create_macro
{
	my $cont = shift;

	# Prevents false matches	
	return $cont if ( ! $Globals::ENV{PRESCAN}->{MACRO});

	
	my $macro = shift @{$Globals::ENV{PRESCAN}->{MACRO}};

	$macro->{SQL} =~ s{:(\w+)}{\{$1\}}g;

	my @format;
	foreach my $arg (@{$macro->{ARGS}})
	{
		push(@format, "$arg=$arg");
	}

	my $template = $CFG_POINTER->{macro_template};
	$template =~ s{%MACRO_NAME%}{$macro->{MACRO_NAME}};
	$template =~ s{%MACRO_PARMS%}{join(',', @{$macro->{ARGS}})}ex;
	$template =~ s{%MACRO_SQL%}{$macro->{SQL}};
	$template =~ s{%MACRO_FORMAT%}{join(',', @format)}ex;
	return "<:nowrap:>$template";
}

sub databricks_notebook_run
{
	my $cont = shift;
	return $cont unless ($cont =~ m{\bCALL\s+([\w.]+)(.*)}si);
	my ($call_name, $call_args) = ($1, $2);

	# Remove everything except actual arg vals from $call_args
	$call_args =~ s{;\s*$}{};
	$call_args =~ s{^\s*\(}{};
	$call_args =~ s{\)\s*$}{};
	my @call_args = split(/,/, $call_args);
	foreach (@call_args)
	{
		s{^\s+}{};
		s{\s+$}{};
	}

	# Get parm info from conversion catalog data. The catalog entries that we need look like this:
	#    stored_procedure_args,<proc_name>,<arg_num>:::<arg_name>,<arg_io_type>,<arg_data_type>
	# E.g.:
	#    stored_procedure_args,NameLookup,0:::Name,IN,CHAR
	#    stored_procedure_args,NameLookup,1:::FullName,OUT,CHAR
	#    stored_procedure_args,CalcTax,0:::Amt,IN,INTEGER
	#    stored_procedure_args,CalcTax,1:::Tax,OUT,DECIMAL

	# my %parms = ();
	my @resultj_parms = ();     # For gathering IN and INOUT arg types for the "_resultJ" in template
	my @result_parms = ();      # For gathering OUT and INOUT arg types for the "_result" in template
	my @result_out_parms = ();  # For gathering CALL stmt args to use in the "_result" in template
	my $found_call = 0;

	# Find the keys that we need (e.g. "stored_procedure_args,CalcTax,<arg_num>")
	foreach my $key (sort(keys(%conv_cat)))
	{
		if ($key =~ m{^stored_procedure_args,$call_name,(.*)})
		{
			$found_call = 1;
			my $parm_num = $1;

			if ($parm_num eq 'x')    # Means that there are no parms!
			{
				$found_call = 'noparms';
				last;
			}

			# Get the parm name, io type (IN / OUT / INOUT), and data type for the key
			my ($parm_name, $parm_io_type, $parm_data_type) = $conv_cat{$key} =~ m{(.*?),(.*?),(.*)};

			# For IN and INOUT types, save the name and value (value is what is in the CALL statement)
			my $parm = ();
			if ($parm_io_type eq 'IN' or $parm_io_type eq 'INOUT')
			{
				$parm->{NAME}  = $parm_name;
				$parm->{VALUE} = $call_args[$parm_num];
				push (@resultj_parms, $parm);
			}

			# Save same for OUT and INOUT
			if ($parm_io_type eq 'OUT' or $parm_io_type eq 'INOUT')
			{
				push(@result_parms, "\"$parm_name\"");
				push(@result_out_parms, $call_args[$parm_num]);
			}
		}
	}

	# Check to see if we got anything for the CALL name (Could be a call to something OTHER than a stored procedure)
	return $cont if ( ! $found_call);

	# If there are no parms, use a specific template for that
	if ($found_call eq 'noparms')
	{
		my $templ = $CFG_POINTER->{notebook_run_noparms_template};
		$templ =~ s{%NOTEBOOK_NAME%}{$call_name}g;

		return "<:nowrap:>$templ";
	}

	# Final _resultJ info
	my @final_resultj_parms;
	foreach my $parm (@resultj_parms)
	{
		push(@final_resultj_parms, "\"$parm->{NAME}\" : str\($parm->{VALUE}\)");
	}

	# Use the saved info to populate the Notebook template
	my $templ = $CFG_POINTER->{notebook_run_template};
	$templ =~ s{%NOTEBOOK_NAME%}{$call_name}g;
	$templ =~ s{%IN_PARMS_RESULTJ%}{join(",\n", @final_resultj_parms) . "\n"}eg;
	$templ =~ s{%IN_PARMS_RESULT%}{join(", ", @result_parms)}eg;
	$templ =~ s{%OUT_PARMS%}{join(", ", @result_out_parms) . ','}eg;

	return "<:nowrap:>$templ";
}

sub databricks_set_variable
# Handle a "SET" statement
{
	my $cont = shift;

	my $check_cont = $cont;
	$check_cont =~ s{^\s*\-\-.*}{}mg;                              # Remove comment lines
	return $cont if ( $check_cont =~ m{^\s*(UPDATE|MERGE)\s}si);   # Ignore if the "SET" is in an UPDATE or MERGE
	return $cont if ( $check_cont =~ m{"""\s*(UPDATE|MERGE)\s}si);    # Could be in already-generated """...""" code

	# "from": "^(\s*(THEN\s+|ELSE\s+)?\s*)SET\s+(\w+\s*\=)", "to": "<:nowrap:>$1$3"
	$cont =~ s{\bSET\s+(\w+\s*\=)}{<:nowrap:>$1}is;

	$Globals::ENV{PRESCAN}->{ALL_VAR_NAMES}->{uc($MR->trim($1))} = 1;

	return $cont;
}

sub is_all_comments_or_blanks
{
	my $cont = shift;
	# print STDERR "Check for comment / blank: $cont\n";
	$cont =~ s{^\s*\-\-.*}{}mg;
	$cont =~ s{/\*.*?\*/}{}sg;

	if ($cont =~ m{\S})
	{
		# print STDERR "   NOT comment / blank\n";
		return 0;
	}
	else
	{
		# print STDERR "   IS comment / blank\n";
		return 1;
	}
}
sub convert_comment 
{
	my $cont = shift;

	######################################################################
	# We can't convert comments (e.g /* style to -- style) because we 
	# will lose track of masked comments !!!!!!!!!!
	######################################################################

	# $cont =~ s{/\*.*?\*/}{convert_comment2($&)}esg;

	return $cont;
}
sub convert_comment2
{
	my $comment = shift;
	$comment =~ s{^/\*}{};
	$comment =~ s{\*/$}{};
	$comment =~ s{^}{--}mg;
	return $comment;
}

sub databricks_sample_percent 
{
	my $cont = shift;

	$MR->log_msg("databricks_sample_percent");

	# Report an error in the log AND in oputput if we don't have what we need
	if ( ! $Globals::ENV{PRESCAN}->{SAMPLE_PERCENT}) 
	{
		$MR->log_error("*** ERROR: Nothing found for handling \"SAMPLE <percent>\"");
		return "--ERROR: This is not being handled properly:\n$cont\n-- END ERROR\n";
		# return "$Globals::ENV{PRESCAN}->{COMMENT_CHAR}ERROR: This is not being handled properly:\n$cont\n$Globals::ENV{PRESCAN}->{COMMENT_CHAR} END ERROR\n";
	}

	# Do a *shift* to get *corresponding push* that we did in the source hook routine
	my $sample_percent_info = shift @{$Globals::ENV{PRESCAN}->{SAMPLE_PERCENT}};

	# my $output_code = '';

	# Convert something like "SAMPLE 0.5, 0.25 ..." to "TABLESAMPLE (50 PERCENT)
	# LIMITATIONS:
	#    - We can only handle the first arg after "SAMPLE", so would be 0.5 in the above

	$sample_percent_info =~ m{(0)?\.([0-9]+)};
	my $num = "0.$2";
	$num = ( 0 + $num ) * 100;
	return "TABLESAMPLE ($num PERCENT)\n";;
}

sub convert_exponent 
# Convert "<expression1> ** <expression2>" to "POW(<expression1>, <expression2>)"
# Note: <expression> can be either a "word", i.e. \w+, or a balanced set of parens
{
	my $cont = shift;
	my $paren_count = 0;

	# Tag the parens
	$cont =~ s{(\(|\))}{parens($1, $paren_count)}eg;

	# Use tagged parens to find and convert to POW format
	$cont =~ s{ ( <BB_LEFT_PAREN:(\d+)BB_LEFT_PAREN>(.*?)<BB_RIGHT_PAREN:(\2)BB_RIGHT_PAREN>  | \w+ ) \s*\*\*\s*  ( <BB_LEFT_PAREN:(\d+)BB_LEFT_PAREN>(.*?)<BBRIGHT_PAREN:(\6)BB_RIGHT_PAREN>  | \w+ )  }{POW($1, $5)}gx;

	# Clean-up (remove tagged parens)
	$cont =~ s{(<BB_LEFT_PAREN:\d+BB_LEFT_PAREN>)}{\(}g;
	$cont =~ s{(<BB_RIGHT_PAREN:\d+BB_RIGHT_PAREN>)}{\)}g;

	return $cont;
}
sub parens 
# Put tags arouind parens
{

	my $paren = shift;
	my $paren_count = shift;
	my $return = '';
	if ($paren eq '(') 
	{
		$paren_count++;
		$return = '<BB_LEFT_PAREN:' .  $paren_count . "BB_LEFT_PAREN>";
	} 
	else 
	{
		$return = '<BB_RIGHT_PAREN:' .  $paren_count . "BB_RIGHT_PAREN>";
		$paren_count--;
	}
	return $return;
}

sub databricks_copy_into
{
	my $cont = shift;
	$MR->log_msg("databricks_copy_into");
	my $instance_num = 1 - $#{$Globals::ENV{PRESCAN}->{IMPORT}};
	my $import_info = shift @{$Globals::ENV{PRESCAN}->{IMPORT}};

	# my $copy_into_template_code = $MR->read_file_content($CFG_POINTER->{data_import_template_file});
	my $copy_into_template_code = '';
	if ($Globals::ENV{PRESCAN}->{BTEQ_MODE})
	{
		$copy_into_template_code = $MR->read_file_content($CFG_POINTER->{copy_into_xsql_template_file});
	}
	else
	{
		$copy_into_template_code = $MR->read_file_content($CFG_POINTER->{copy_into_sparksql_template_file});
	}

	$copy_into_template_code =~ s{__END__.*}{}si;  # Remove everything from __END__ onward
	if ( ! $copy_into_template_code) 
	{
		$MR->log_error("\n****************************\n"
		           . "*** ERROR: Cannot convert this source:\n$import_info->{ORIGINAL_SOURCE}"
		           . "*** REASON: Missing attribute \"data_import_template\" in config. Should look something like this: "
			. 'COPY INTO %TABLE_NAME% \nFROM (\n SELECT \n%COLUMN_NAMES%\n FROM %FILE_NAME%\n)\nFILEFORMAT = CSV\nDELIMITER = \"%DELIMITER%\"\n;'
		    . "\n****************************");
	}

	# We need: Table name, File name, "USING" clause, "INSERT" clause, Delimiter
	my $bad_copy_into = 0;
	foreach my $attribute ('TABLE_NAME', 'FILE_NAME')   # Took out 'INSERT' and 'DELIMITER': won't be present for "IMPORT DATA". Also 'USING'
	{
		if ( ! $import_info->{$attribute}) 
		{
			# report as error
			$MR->log_error("Attribute \"$attribute\" not found during generation of COPY INTO");
			$bad_copy_into = 1;
		}
	}
	if ($bad_copy_into) 
	{
		$copy_into_template_code = "--FIXME Found unsupported source configuration during generation of COPY INTO.\n"
		                  . "/* Original source:\n"
		                  . $import_info->{ORIGINAL_SOURCE}
		                  . "*/\n";
		return $copy_into_template_code;
	} 
	# Foreach "attribute" (e.g. "TABLE_NAME", "FILE_NAME", etc) in $Globals::ENV{PRESCAN}->{IMPORT}->{<attribute>}
	foreach my $attribute (keys(%{ $import_info })) 
	{
		# Convert the matching %<attribute>% values in the template, e.g. %TABLE_NAME% changes to value of $Globals::ENV{PRESCAN}->{IMPORT}->{TABLE_NAME}
		$copy_into_template_code =~ s{%$attribute%}{$import_info->{$attribute}}g;
	}

	my @select_cols = get_infile_select_cols($import_info->{INFILE_COLS}, $import_info->{MAP_COL_NAMES}, 
								$import_info->{DELIMITER}, $import_info->{VALUES_BY_COL_NAME});
	$import_info->{DELIMITER} ? $copy_into_template_code =~ s{%FILE_FORMAT%}{CSV} 
							  : $copy_into_template_code =~ s{%FILE_FORMAT%}{PARQUET};

	# Convert 
	my $select_cols_str = convert_dml(join(",\n", @select_cols));

	# Remove tagging info for conditional tags, e.g.: <?sometag:>...</sometag>
	foreach my $optional_tag ('DELIMITER', 'BAD_RECS_PATH')
	{
		if ($import_info->{$optional_tag})   # If the tag was used then delete the conditional tags
		{
			$copy_into_template_code =~ s{<\?$optional_tag:>}{}g;
			$copy_into_template_code =~ s{</$optional_tag>}{}g;
		} 
		else                                 # The tag was not used, so delete everything between the conditional tags
		{
			$copy_into_template_code =~ s{<\?$optional_tag:>.*?</$optional_tag>}{}sg;
		}
	}

	$copy_into_template_code =~ s{%COLUMN_NAMES%}{$select_cols_str};

	# Remove code that is conditional on a contained %...% tag not being set. e.g. if we have this:
	#    OPTIONS: <?MYTAG:> X=1 Y=2 SOMEVALUE=%MYTAG%, %OTHER_TAG%</MYTAG> END
	# And %MYTAG% gets left as %MYTAG% (i.e. not converted to anything), then what's left will be:
	#    OPTIONS:  END
	$copy_into_template_code =~ s{<\?(\w+):>.*?%\1%.*?</\1>}{}g;

	# Clean up left-over comma (comma before right paren)
	$copy_into_template_code =~ s{,(\s*\))}{$1};

	$copy_into_template_code =~ s{%NUM%}{$instance_num}g;

	# Report any unused %...% tags 
	if ($copy_into_template_code =~ m{\%\w+\%}) 
	{
		$MR->log_error("Warning: Unused \"\%...\%\" tag(s) in data_import_template in config resulted in this output:\n  $copy_into_template_code");

	} 
	# return $copy_into_template_code;
	return "<:nowrap:>$copy_into_template_code";
}

sub databricks_merge_into
# For doing MERGE INTO (although we could end up doing COPY INTO)
{
	my $cont = shift;
	$MR->log_msg("databricks_copy_into");
	my $instance_num = 1 - $#{$Globals::ENV{PRESCAN}->{MLOAD}};
	my $merge_info = shift @{$Globals::ENV{PRESCAN}->{MLOAD}};
	my $merge_into_template_code = '';
	if ($Globals::ENV{PRESCAN}->{BTEQ_MODE})
	{
		$merge_into_template_code = $MR->read_file_content($CFG_POINTER->{merge_into_xsql_template_file});
	}
	else
	{
		$merge_into_template_code = $MR->read_file_content($CFG_POINTER->{merge_into_sparksql_template_file});
	}
	$merge_into_template_code =~ s{__END__.*}{}si;  # Remove everything from __END__ onward

	# "Global" things (i.e. we don't need to drill down to find them, although they might end up not coming out)
	$merge_into_template_code =~ s{%NUM%}{$instance_num}g;
	$merge_into_template_code =~ s{%FILE_NAME%}{$merge_info->{IMPORT}->{INFILE_NAME}}g;
	# $merge_into_template_code =~ s{%DELIMITER%}{"$merge_info->{IMPORT}->{DELIMITER}"}g;
	$merge_info->{IMPORT}->{DELIMITER} ? $merge_into_template_code =~ s{%FORMAT%}{CSV} 
	                                   : $merge_into_template_code =~ s{%FORMAT%}{PARQUET};

	# Don't think we need this
	my $merge_into_template_code_orig = $merge_into_template_code;  # Save template for re-use

	# Get all sections into separate merge-type-specific code blocks, deleting them from the main template.
	# Then as we check for each "APPLY" operation and change its template code, we will put the changed template code back 
	# into the main template, appending to the main template as we go
	my ($view_for_merge_template, $merge_upsert_template, $merge_copy_into_template, $merge_update_template, $merge_delete_template) = ('','','','','');
	# $merge_into_template_code =~ s{\n\s*<\?VIEW_FOR_MERGE:> (.*) </VIEW_FOR_MERGE>} {}xsig && ($view_for_merge_template  = $1);
	$merge_into_template_code =~ s{\n\s*<\?MERGE_UPSERT:>   (.*) </MERGE_UPSERT>  } {}xsig && ($merge_upsert_template    = $1);
	$merge_into_template_code =~ s{\n\s*<\?COPY_INTO:>      (.*) </COPY_INTO>     } {}xsig && ($merge_copy_into_template = $1);
	$merge_into_template_code =~ s{\n\s*<\?MERGE_UPDATE:>   (.*) </MERGE_UPDATE>  } {}xsig && ($merge_update_template    = $1);
	$merge_into_template_code =~ s{\n\s*<\?MERGE_DELETE:>   (.*) </MERGE_DELETE>  } {}xsig && ($merge_delete_template    = $1);

	# For each "APPLY" we will do a MERGE or COPY INTO
	my $need_view = 0;
	foreach my $apply ( @{ $merge_info->{IMPORT}->{APPLY} })
	{
		my $apply_op   = $apply->{DML_LABEL};
		my $apply_cond = $apply->{COND};

		# ** UPSERT ** - An INSERT AND an UPDATE become an UPSERT (WHEN MATCHED THEN UPDATE...WHEN NOT MATCHED THEN INSERT...)
		if ($merge_info->{DML_LABEL}->{$apply_op}->{INSERT} && $merge_info->{DML_LABEL}->{$apply_op}->{UPDATE})
		{
			my $new_merge_upsert_template = $merge_upsert_template;  # Create a new copy of the upsert template

			#---------- "SELECT" 
			my @select_cols = get_infile_select_cols($merge_info->{LAYOUT}->{INFILE_COLS}, $merge_info->{DML_LABEL}->{$apply_op}->{MAP_COL_NAMES},
						$merge_info->{IMPORT}->{DELIMITER}, $merge_info->{DML_LABEL}->{$apply_op}->{INSERT}->{VALUES_BY_COL_NAME});

			my $select_cols_str = convert_dml(join(",\n", @select_cols));

			$new_merge_upsert_template =~ s{%TITLE%}{$apply_op};
			$new_merge_upsert_template =~ s{%TABLE_NAME%}{$merge_info->{DML_LABEL}->{$apply_op}->{TABLE_NAME}};
			$new_merge_upsert_template =~ s{%COLUMN_NAMES%}{$select_cols_str};

			#---------- "ON"
			# Get the MERGE "ON" clause from the UPDATE's WHERE clause
			my ($merge_on)     = $merge_info->{DML_LABEL}->{$apply_op}->{UPDATE}->{SQL} =~ m{\sWHERE\s+ (.*?) ( ; | $ )}sxi;

			# Prefix the WHERE column names with "t." (target) or "s." (source)
			$merge_on =~ s{(\w+\s*=)}{t.$1}g;
			$merge_on =~ s{:}{s.}g;

			$new_merge_upsert_template =~ s{%ON%}{$merge_on};

			#---------- "WHEN MATCHED THEN UPDATE"
			# Get the "WHEN MATCHED THEN UPDATE SET..." from the UPDATE's SET clause
			my ($merge_update) = $merge_info->{DML_LABEL}->{$apply_op}->{UPDATE}->{SQL} =~ m{\sSET\s+   (.*?) ( ; | WHERE | $ )}sxi;

			# Prefix the UPDATE source column names with "s." (source)
			$merge_update =~ s{:}{s.}g;

			$new_merge_upsert_template =~ s{%UPDATE_SET%}{$merge_update};

			#---------- "WHEN NOT MATCHED THEN
			#            INSERT"
			# Get the "WHEN NOT MATCHED THEN INSERT..." from the INSERT's column names
			my ($merge_insert) = $merge_info->{DML_LABEL}->{$apply_op}->{INSERT}->{SQL} =~ m{\bINSERT\s+INTO\s+[\w.]+\s*\( (.*?) \)}sxi;
			$new_merge_upsert_template =~ s{%INSERT_COLUMN_NAMES%}{$merge_insert};

			#---------- "VALUES"
			# Get the "WHEN NOT MATCHED THEN INSERT... VALUES..." (the VALUES... part) from the INSERT's VALUES clause
			my ($merge_values) = $merge_info->{DML_LABEL}->{$apply_op}->{INSERT}->{SQL} =~ m{\bVALUES\s*\( (.*?) \)}sxi;

			# Prefix the VALUES column names with "s." (source)
			$merge_values =~ s{:}{s.}g;

			$new_merge_upsert_template =~ s{%INSERT_VALUES%}{$merge_values};

			# Put the modified code back into the main template. We also need the VIEW template code
			$merge_into_template_code .= $new_merge_upsert_template;
			$need_view = 1;
		}

		# An INSERT on its own becomes a COPY INTO
		elsif ($merge_info->{DML_LABEL}->{$apply_op}->{INSERT})
		{
			my $new_merge_copy_into_template = $merge_copy_into_template;

			#---------- "SELECT" 
			my @select_cols = get_infile_select_cols($merge_info->{LAYOUT}->{INFILE_COLS}, $merge_info->{DML_LABEL}->{$apply_op}->{MAP_COL_NAMES},
						$merge_info->{IMPORT}->{DELIMITER}, $merge_info->{DML_LABEL}->{$apply_op}->{INSERT}->{VALUES_BY_COL_NAME});

			# Convert 
			my $select_cols_str = convert_dml(join(",\n", @select_cols));

			$new_merge_copy_into_template =~ s{%TITLE%}{$apply_op};
			$new_merge_copy_into_template =~ s{%TABLE_NAME%}{$merge_info->{DML_LABEL}->{$apply_op}->{TABLE_NAME}};
			$new_merge_copy_into_template =~ s{%COLUMN_NAMES%}{$select_cols_str};

			$merge_info->{IMPORT}->{DELIMITER} ? $new_merge_copy_into_template =~ s{%FILE_FORMAT%}{CSV} 
			                                   : $new_merge_copy_into_template =~ s{%FILE_FORMAT%}{PARQUET};

			# Put the modified code back into the main template
			$merge_into_template_code .= $new_merge_copy_into_template;
		}

		# An UPDATE on its own becomes a MERGE...WHEN MATCHED THEN UPDATE
		elsif ($merge_info->{DML_LABEL}->{$apply_op}->{UPDATE})
		{
			my $new_merge_update_template = $merge_update_template;  # Create a new copy of the update template

			#---------- "SELECT" 
			my @select_cols = get_infile_select_cols($merge_info->{LAYOUT}->{INFILE_COLS}, $merge_info->{DML_LABEL}->{$apply_op}->{MAP_COL_NAMES},
						$merge_info->{IMPORT}->{DELIMITER}, $merge_info->{DML_LABEL}->{$apply_op}->{INSERT}->{VALUES_BY_COL_NAME});

			my $select_cols_str = convert_dml(join(",\n", @select_cols));

			$new_merge_update_template =~ s{%TITLE%}{$apply_op};
			$new_merge_update_template =~ s{%TABLE_NAME%}{$merge_info->{DML_LABEL}->{$apply_op}->{TABLE_NAME}};
			$new_merge_update_template =~ s{%COLUMN_NAMES%}{$select_cols_str};

			# The APPLY operation points to the WHERE condition
			my $select_where = $apply_cond;

			$new_merge_update_template =~ s{%WHERE%}{$select_where};

			#---------- "ON"
			# Get the MERGE "ON" clause from the UPDATE's WHERE clause
			my ($merge_on)     = $merge_info->{DML_LABEL}->{$apply_op}->{UPDATE}->{SQL} =~ m{\sWHERE\s+ (.*?) ( ; | $ )}sxi;

			# Prefix the WHERE column names with "t." (target) or "s." (source)
			$merge_on =~ s{(\w+\s*=)}{t.$1}g;
			$merge_on =~ s{:}{s.}g;

			$new_merge_update_template =~ s{%ON%}{$merge_on};

			#---------- "WHEN MATCHED THEN UPDATE"
			# Get the "WHEN MATCHED THEN UPDATE SET..." from the UPDATE's SET clause
			my ($merge_update) = $merge_info->{DML_LABEL}->{$apply_op}->{UPDATE}->{SQL} =~ m{\sSET\s+   (.*?) ( ; | WHERE | $ )}sxi;

			# Prefix the UPDATE source column names with "s." (source)
			$merge_update =~ s{:}{s.}g;

			$new_merge_update_template =~ s{%UPDATE_SET%}{$merge_update};

			# Put the modified code back into the main template. We also need the VIEW template code
			$merge_into_template_code .= $new_merge_update_template;
			$need_view = 1;
		}

		# A DELETE becomes a MERGE...WHEN MATCHED THEN DELETE
		elsif ($merge_info->{DML_LABEL}->{$apply_op}->{DELETE})
		{
			my $new_merge_delete_template = $merge_delete_template;  # Create a new copy of the delete template

			#---------- "SELECT" 
			my @select_cols = get_infile_select_cols($merge_info->{LAYOUT}->{INFILE_COLS}, $merge_info->{DML_LABEL}->{$apply_op}->{MAP_COL_NAMES},
						$merge_info->{IMPORT}->{DELIMITER}, $merge_info->{DML_LABEL}->{$apply_op}->{INSERT}->{VALUES_BY_COL_NAME});

			my $select_cols_str = convert_dml(join(",\n", @select_cols));

			$new_merge_delete_template =~ s{%TITLE%}{$apply_op};
			$new_merge_delete_template =~ s{%TABLE_NAME%}{$merge_info->{DML_LABEL}->{$apply_op}->{TABLE_NAME}};
			$new_merge_delete_template =~ s{%COLUMN_NAMES%}{$select_cols_str};

			# The APPLY operation points to the WHERE condition
			my $select_where = $apply_cond;
			$new_merge_delete_template =~ s{%WHERE%}{$select_where};

			#---------- "ON"
			# Get the MERGE "ON" clause from the DELETE's's WHERE clause
			my ($merge_on)     = $merge_info->{DML_LABEL}->{$apply_op}->{DELETE}->{SQL} =~ m{\sWHERE\s+ (.*?) ( ; | $ )}sxi;

			# Prefix the WHERE column names with "t." (target) or "s." (source)
			$merge_on =~ s{(\w+\s*=)}{t.$1}g;
			$merge_on =~ s{:}{s.}g;

			$new_merge_delete_template =~ s{%ON%}{$merge_on};

			# Put the modified code back into the main template. We also need the VIEW template code
			$merge_into_template_code .= $new_merge_delete_template;
			$need_view = 1;
		}
	}

	# If we need the CREATE VIEW... (which we will if we created any MERGEs)
	if ($need_view)
	{
		if ($merge_info->{IMPORT}->{DELIMITER})     # Need the options related to CSV type processing
		{
			$merge_into_template_code =~ s{%DELIMITER%}{"$merge_info->{IMPORT}->{DELIMITER}"};

			# Don't leave blank lines
			$merge_into_template_code =~ s{^\s*<\?DELIMITER:>\s*\n}{}mig;  
			$merge_into_template_code =~ s{^\s*</DELIMITER>\s*\n}{}mig;

			# ...Othwerwise
			$merge_into_template_code =~ s{<\?DELIMITER:>}{}ig;
			$merge_into_template_code =~ s{</DELIMITER>}{}ig;
		}
		else                                        # Don't need the options related to CSV type processing
		{
			$merge_into_template_code =~ s{^\s*<\?DELIMITER:>.*?</DELIMITER>\s*\n}{}sig;   # Don't leave blank lines
			$merge_into_template_code =~ s{<\?DELIMITER:>.*?</DELIMITER>}{}sig;            # ...Otherwise
		}
		$merge_into_template_code =~ s{<\?VIEW_FOR_MERGE:>}{}ig;
		$merge_into_template_code =~ s{</VIEW_FOR_MERGE>}{}ig;

	}
	else  # Don't need the VIEW
	{
		$merge_into_template_code =~ s{\n\s*<\?VIEW_FOR_MERGE:> .* </VIEW_FOR_MERGE>}{}xsig;
	}

	return "<:nowrap:>" . $merge_into_template_code;
}

sub get_infile_select_cols
# Create a SELECT columns list by traversing the column defs that are passed (these are cols in def of an input file),
# figuring out (using the passed col names mapping and values) how to construct each returned column def.
# We also need to create column defs differently for delimited files vs not (Parquet)
{
	my $infile_column_defs = shift;      # From an input file layout
	my $map_col_names = shift;           # Map cols in INSERT to cols in VALUES / Input file
	my $delimiter = shift;               # Indicates whether input file is CSV type or not  (Parquet)
	my $values_by_col_name = shift;      # Hash of VALUES-col-name => VALUES-col-def (as opposed to VALUES array)
	
	my @select_cols = ();  # We will create and return this

	my $csv_col_num = 0;
	# Process columns in order of how they appear in the original input file layout
	foreach my $col_num (sort {$a <=> $b} (keys(%{ $infile_column_defs })))
	{ 
		my $infile_col_name = $infile_column_defs->{$col_num}->{COL_NAME};
		my $insert_col_name = $map_col_names->{$infile_col_name};
		if ($delimiter) 
		{
			# push(@select_cols, "$values_by_col_name->{$infile_col_name} as " . $insert_col_name);
			# The column order for delimited data is just _c0, _c1, etc
			# push(@select_cols, "_c$csv_col_num as " . $insert_col_name);

			# ... but we still need the info from $values_by_col_name, because it might contain something like 
			# "FORMAT (...)"
			my $select_col = $values_by_col_name->{$infile_col_name};
			$select_col =~ s{\b$infile_col_name\b}{_c$csv_col_num};
			push(@select_cols, "$select_col as $insert_col_name");

			$csv_col_num++;
		}
		else
		{
			my $select_col = $infile_column_defs->{$col_num}->{COL_NAME};
			my %casts_convert = (INTEGER => 'INTEGER', DATE => 'DATE', BYTE => 'BINARY', VARBYTE => 'BINARY', BLOB => 'BINARY', 
				                 CLOB  => 'STRING', BYTEINT => 'BYTE', 'LONG\s+VARCHAR' => 'STRING');
			foreach my $cast_type (keys %casts_convert)
			{
				if ($infile_column_defs->{$col_num}->{DATA_TYPE} =~ m{^$cast_type$}i)
				{
					$select_col .= "::$casts_convert{$cast_type} as " . $infile_column_defs->{$col_num}->{COL_NAME};
				}
			}
			push(@select_cols, $select_col);
		}
	}
	return @select_cols;
}

sub databricks_insert_overwrite
{
	my $cont = shift;
	$MR->log_msg("databricks_insert_overwrite");
	my $instance_num = 1 - $#{$Globals::ENV{PRESCAN}->{EXPORT}};
	my $export_info = shift @{$Globals::ENV{PRESCAN}->{EXPORT}};

	my $insert_overwrite_template_code = $MR->read_file_content($CFG_POINTER->{insert_overwrite_template_file});
	$insert_overwrite_template_code =~ s{__END__.*}{}si;  # Remove everything from __END__ onward

	# Convert 
	my $select_statement = convert_dml($export_info->{SELECT_STATEMENT});

	# Foreach "attribute" (e.g. "TABLE_NAME", "FILE_NAME", etc) in $Globals::ENV{PRESCAN}->{EXPORT}->{<attribute>}
	foreach my $attribute (keys(%{ $export_info })) 
	{
		# Convert the matching %<attribute>% values in the template, e.g. %TABLE_NAME% changes to value of $Globals::ENV{PRESCAN}->{EXPORT}->{TABLE_NAME}
		$insert_overwrite_template_code =~ s{%$attribute%}{$export_info->{$attribute}}g;
	}

	$insert_overwrite_template_code =~ s{%NUM%}{$instance_num}g;

	return "<:nowrap:>$insert_overwrite_template_code";
}

#Subroutine for SQL dks to push widget at top of output before calling databricks_finalize_code to add notebook divisor
sub databricks_finalize_sql
{
	my $ar = shift;
	my $options = shift;

	$MR->log_msg("STARTING DATABRICKS FINALIZE SQL: " . Dumper($ar) . "OPtions: " . Dumper($options) . "\nWIDGETS: " . Dumper($ENV{WIDGET}));

	# $ar = $ENV{WIDGET} . $ar;
	# Insert "CREATE WIDGET..." code as first element in $ar ARRAY 
	unshift(@$ar, $ENV{WIDGET});
	databricks_finalize_code($ar,$options);
	return $ar; 
}

sub databricks_finalize_code
{
	my $ar = shift;
	my $options = shift;
	
	return unless  $CFG_POINTER->{use_notebook_md};
	return unless $CFG_POINTER->{consolidate_nb_statements};

	# If the output code has any "Notebook Initialize" blocks, create a Notebook cell
	# for them at the top of the code and move them there. This ensures that all
	# widgets (dbutils.widgets.text(...) are set in one logical place
	if (grep(/#\s*BEGIN\s+Notebook\s+Init/i, @{$ar}))                     # If any "Notebook Init"s...
	{
		unshift(@{$ar}, '<:nowrap:>');                                    # ...insert a new first cell
		foreach my $frag (@{$ar})
		{
			while ($frag =~ s{\#\s*BEGIN\s+Notebook\s+Init.*?\n           # ...remove "Notebook init"
				               (.*?)
				              \#\s*END\s+Notebook\s+init.*?\n}{}xsig)     # block, and...
			{
				$ar->[0] .= $1;                                           # ... add the bits between
			}                                                             # to the first cell
		}
	}

	my @new_stmt_array = ();
	# Put multi-line(frag) comments into one fragment
	my @comment_block = ();
	my $comment_block = '';
	foreach my $fr(@$ar) {
		if (is_all_comments_or_blanks($fr)) {
			push(@comment_block, $fr)
		} else {
			if (@comment_block) {
				my $comment_block = join(' ', @comment_block);
				push (@new_stmt_array, $comment_block);
				@comment_block = ();
				push (@new_stmt_array, $fr);
			} else {
				push (@new_stmt_array, $fr);
			}
		}
	}
	if (@comment_block) {
		my $comment_block = join(' ', @comment_block);
		push (@new_stmt_array, $comment_block);
	}

	while (scalar(@$ar) >= 1) {shift(@$ar);} #blank out the array.  Can't assign a new array, bc it is passed by ref

	foreach my $fr (@new_stmt_array)
	{
		my $final_fr = databricks_wrap_statement($fr);
		push(@$ar, $final_fr);
	}

	# Change array: 
	#    n:   --FIXME...
	#    n+1: (\-\-|#)\s*COMMAND ---------
	# to    
	#    n+1: --FIXME...
	#         $1 COMMAND ----------
	my $count = 0;
	foreach my $fr (@$ar)
	{
		# If this element is FIXME and next element is -- COMMAND
		if ($fr =~ m{^(\s*\-\-\s*)FIXME(.*)}m && $ar->[$count + 1] =~ m{^(\s*\-\-|\#)\s*COMMAND\s*\-+})
		{
			# Remove FIXME from this element
			$fr =~ s{^(\s*\-\-\s*)FIXME(.*)}{}m;
			my $fixme = "$1<:fixme:>$2";

			# ...and add it to beginning of next element
			$ar->[$count + 1] =~ s{^((\s*\-\-|\#)\s*COMMAND\s*\-+)}{$1\n$fixme\n};
		}
		$count++;
	}

	foreach (@$ar) {
		s{<:fixme:>}{FIXME}g;
	}


	if ($CFG_POINTER->{global_substitutions}) 
	{
		foreach my $fr (@$ar) 
		{
			foreach my $gsub (@{ $CFG_POINTER->{global_substitutions}  })
			{
				if ($gsub->{extension_call})
				{
					if ($fr =~ m{$gsub->{from}})
					{
						my $subroutine_name = substr($gsub->{extension_call}, 2);
						if (exists &{$subroutine_name})
						{
							my $replacement = &$subroutine_name($gsub->{from});
							$fr =~ s{$gsub->{from}}{$replacement};
						}
						else
						{
							$MR->log_error("\n**************** ERROR ***************\n"
							             . "extension_call \"$gsub->{extension_call}\" does not exist\n"
							             . Dumper($gsub) );
						}
					}
				}
				else
				{
					my $eval_gsub = "my \$gsub_count = 0; while (\$fr =~ s{$gsub->{from}}{$gsub->{to}}sgi) {die \"Global substitution stuck in loop!!\" if \$gsub_count++ > 1000}";
					eval ($eval_gsub);
					my $ret = $@;
					if ($ret)
					{
						$MR->log_error("************ EVAL ERROR in global substitution: $ret ************");
						$MR->log_error("*** Failing eval code: $eval_gsub");
						$MR->log_error("*** Input to substitution (\$fr): $fr\n");
						exit -1;
					}
				}
			}
		}
	}

	# Convert "--<indent..." to actual indent spaces
	my $indent_count = 0;
	my $indent_spaces = '';
	foreach my $fr (@$ar) 
	{
		my $new_fr = '';
		foreach my $line (split(/(\n)/, $fr))
		{
			next if ($line =~ m{(s_p_i_f|s_p_e_n_d_i_f)});   # Remove these tags

			# We can't have separate Notebook Cells ("# COMMAND...") in indented code
			if ($indent_count > 0)
			{
				next if ($line =~ m{^\s*(\#|\-\-)\s*COMMAND\b});
			}
		   if ($line =~ m{\-\-<indent\+\+>})           # Indent more
		   {
		      $indent_count++;
		      next;
		      # $line =~ s{<indent\+\+>}{};
		   } 
		   elsif ($line =~ m{\-\-<indent\-\->})        # Indent less
		   {
		      $indent_count--;
		      next;
		   } 
		   elsif ($line =~ m{\-\-<indent=0>})            # No indent (back to first column)
		   {
		      $indent_count = 0;
		      # $line =~ s{<indent=0>}{};
		      next;
		   }
		   $indent_spaces = '  ' x $indent_count;      # Each indent is two spaces
		   $line = $indent_spaces . $line;
		   $new_fr .= $line;
		}
		$fr = $new_fr;
	}

	# Do changes in reverse order, ***with NO "g" modifier***, deleting, to avoid dups
	foreach my $fr (reverse(@$ar)) 
	{
		# Added this loop to do in reverse (necessary?) order of key number in comments hash
		my $numkeys = scalar(keys(%{$Globals::ENV{PRESCAN}->{COMMENTS}}));
		foreach my $keynum (reverse(1..$numkeys)) {

			if ($fr =~ m{\-\-<<<c_o_m_m_e_n_t:})
			{
				# Convert masked comments marked as "<:sql_comment:>" back to orig "--" 
				$fr =~ s{\-\-<<<c_o_m_m_e_n_t:\s+($keynum)<:sql_comment:>}{$Globals::ENV{PRESCAN}->{COMMENTS}->{$1}}
				                                                 && delete($Globals::ENV{PRESCAN}->{COMMENTS}->{$1});

				# Convert remaining masked comments to "--" or "#" style, depending on SQL wrapper
				if ($Globals::ENV{PRESCAN}->{use_sql_statement_wrapper})
				{
					$fr =~ s{\-\-<<<c_o_m_m_e_n_t:\s+($keynum)(?=[^0-9]|$ )}{\# <:pycomment:> $Globals::ENV{PRESCAN}->{COMMENTS}->{$1}}x
					                                                   && delete($Globals::ENV{PRESCAN}->{COMMENTS}->{$1});
					$fr =~ s{\# <:pycomment:> }{\# }g;
				}
				else
				{
					$fr =~ s{\-\-<<<c_o_m_m_e_n_t:\s+($keynum)(?=[^0-9]|$ )}{$Globals::ENV{PRESCAN}->{COMMENTS}->{$1}}x
					                                 && delete ($Globals::ENV{PRESCAN}->{COMMENTS}->{$1});
				}
			} 
		}
	}
	# Restore C single-line comments (these can'y be done in reverse order)
	foreach my $fr (@$ar) 
	{
		if ($fr =~ m{/\*<<<c_o_m_m_e_n_t:})
		{
			$fr =~ s{/\*<<<c_o_m_m_e_n_t:\s+([0-9]+)\*/}{$Globals::ENV{PRESCAN}->{COMMENTS_C_SINGLE_LINE}->{$1}}g
			                                   && delete($Globals::ENV{PRESCAN}->{COMMENTS_C_SINGLE_LINE}->{$1});
		}
	}

	foreach my $fr (@$ar) 
	{
		# Remove any extraneous <:sql_comment:> tags (Happens if we add comments like --FIXME, which are not masked)
		$fr =~ s{<:sql_comment:>}{}g;

		# Remove other extraneous comments (these are erroneous dups)
		$fr =~ s{^.*?<<<c_o_m_m_e_n_t:.*?(\n|$ )}{}xmg;
                                         #^^^^^^ Needs to be (\n|$) at end. Else we end up w/ some blanmk lines
	}

	# try: ... except: ... must all be in one Notebook cell, i.e., no "# COMMAND ----------" dividers allowed
	my $got_a_try = 0;
	foreach my $fr (@$ar) 
	{
		if ($fr =~ m{\# COMMAND ----------\n\s*try:})
		{
			$got_a_try = 1;   # We will start removing "# COMMAND ----------" dividers from now on
			next;
		}
		if ($got_a_try)
		{
			$fr =~ s{^\s*\# COMMAND ----------\s*\n}{}mg;
		}
	}

	# Append any end bits
	push(@$ar, @{ $Globals::ENV{PRESCAN}->{NOTEBOOK_END} }) if ($Globals::ENV{PRESCAN}->{NOTEBOOK_END});

	# Convert all variable names to upper case
	#--------------------- Not doing this now ---------------------
	# foreach my $var_name (keys %{ $Globals::ENV{PRESCAN}->{ALL_VAR_NAMES} })
	# {
	# 	foreach my $fr (@$ar) 
	# 	{
	# 		$fr =~ s{\b$var_name\b}{adjust_var_name($var_name, $&, $`, $')}eig;
	# 	}
	# }

	if ($Globals::ENV{PRESCAN}->{use_sql_statement_wrapper})
	{
		$ar->[0] = "$CFG_POINTER->{python_header}\n" . $ar->[0];
		$CFG_POINTER->{target_file_extension} = 'py';
	}
	else
	{
		$CFG_POINTER->{target_file_extension} = 'sql';
	}

	# Adjust comment symbol
	foreach my $fr (@$ar) 
	{
		if ($CFG_POINTER->{target_file_extension} eq 'py')
		{
			$fr =~ s{/\*(.*?)\*/}{#$1}mg;
			$fr =~ s{\-\-(.*?)}{#$1}mg;
			$fr =~ s{\# COMMAND \#\#\#\#\#}{# COMMAND ----------}mg;
		}
		else
		{
			# $fr =~ s{<\# comments>}{ < -- comments >}    # (Not sure if we need this)
		}
	}

	my $whole_cont = join("\nzxasqwzxasqw\n", @$ar);  # Join on a unique marker

	$whole_cont =~ s{<<<:INSERT_OVERWRITE_TABLE:>>>}{INSERT OVERWRITE TABLE}g;

	# SQL comments inside Spark """ strings need to be (possibly converted BACK to) "--" format
	$whole_cont =~ s{ ( (xSqlStmt.query|xSqlStmt.execute|spark.sql)\s*\(\s*""" |  export_sqlstr_[0-9]+\s*=\s*""" )
    	             .*?\n\s*"""
    	            } {convert_comments_to_sql($&)}xsegi;

	while (scalar(@$ar) >= 1) {shift(@$ar);} #blank out the array.  Can't assign a new array, bc it is passed by ref

	foreach my $frag (split(/\nzxasqwzxasqw\n/, $whole_cont))
	{
		$frag =~ s{^zxasqwzxasqw.*?\n}{}mg;
		push(@{$ar}, $frag);
	}

	if ($Globals::ENV{PRESCAN}->{BTEQ_MODE})
	{
		# Insert static cell required for BTEQ
		unshift(@{$ar}, $CFG_POINTER->{bteq_run_xsqlstmt});
	}
}
sub convert_if_to_single_cell
{
	my $cont = shift;
	$cont =~ s{^\s*\#s_p_i_f.*?\n}{}mg;
	$cont =~ s{^\s*\# COMMAND\b.*?\n}{}mg;
	$cont =~ s{^\s*\#s_p_e_n_d_i_f.*?(\n)?}{}mg;   # Note: last one might not have line feed
	return $cont;
}
sub convert_comments_to_sql 
{
	my $cont = shift;
	# Change # comment to SQL
	$cont =~ s{\#(.*)}{--$1}g;
	return $cont;
}
sub convert_sql_comments_to_python 
{
	my $cont = shift;
	# Change "--" SQL comment to "#" python comment
	$cont =~ s{^\s*\-\-}{#}g;
	$cont =~ s{\n\s*\-\-}{\n#}g;
	return $cont;
}
sub adjust_var_name
# Convert a variable name to upper case if it occurs in the right place
{
	my $var_name = shift;
	my $match = shift;
	my $bef = shift;
	my $aft = shift;

	# Get the upper case version of var name
	my $uc_var_name = uc($match);

	return $var_name if ($uc_var_name eq $match);  # Return var name if already upper case

	# Convert if surrounded by {}
	return $uc_var_name if ($bef =~ m{\{\s*$} && $aft =~ m{^\s*\}});

	# Convert if not inside single or double quotes
	$bef =~ s{.*$match}{}si;
	$aft =~ s{$match .*}{}si;
	my $context = $bef . $match . $aft;
	$context =~ s{(['"]).*?\1}{}sg;
	return $uc_var_name if ($context =~ m{\b$var_name\b}i);

	return $match;   # Default to no conversion
}

sub databricks_wrap_statement
{
	my $sql = shift;


	#---- Comment out BEGIN / END that we don't need
	# Don't do "BEGIN\s*(" / "END\s*("
	$sql =~ s{BEGIN\s*\(}{B_E_G_I_N_P_A_R_E_N}sig; 
	$sql =~ s{END\s*\(}{E_N_D_P_A_R_E_N}sig; 

	# Don't do "END REPEAT"
	$sql =~ s{END\s*REPEAT\b}{E_N_D_R_E_P_E_A_T}sig; 

	# Comment out BEGIN 
	$sql =~ s{^\s*((\w+):)?\s*BEGIN\b}{--$1 BEGIN}sig;
	$sql =~ s{\n\s*((\w+):)?\s*BEGIN\b}{\n--$1 BEGIN}sig;

	# Don't do "END CASE"
	$sql =~ s{\bEND\s+CASE\b}{E_N_D_C_A_S_E}sig;

	# Don't do SQL "CASE...END"
	if ($sql =~ m{\bCASE\s.*?\bEND\b}si)
	{
	}
	else
	{
		# Comment out "END"
		$sql =~ s{^\s*END}{--END}sig;
		$sql =~ s{\n\s*END}{\n--END}sig;
	}
	# Restore
	$sql =~ s{E_N_D_C_A_S_E}{END CASE}sig;
	$sql =~ s{B_E_G_I_N_P_A_R_E_N}{BEGIN (}sig;
	$sql =~ s{E_N_D_P_A_R_E_N}{END (}sig;
	$sql =~ s{E_N_D_R_E_P_E_A_T}{END REPEAT}sig;

	if ($Globals::ENV{PRESCAN}->{use_sql_statement_wrapper})
	{
		if ($sql =~ s{<:nowrap:>}{}g)    # Don't wrap if explicit "<:nowrap:>" present (and remove the "<:nowrap:>")
		{
			$sql =~ s{;\s*$}{};          # And remove potential semi-colon at end
		}
		elsif (is_all_comments_or_blanks($sql))
		{
		}
		else
		{
			my $sql_wrapper_template = '';
			if ($sql =~ m{^\s*SELECT\s}i)
			{
				# $sql_wrapper_template = $CFG_POINTER->{xsql_dql_wrapper}; 

				# BTEQ_MODE means we need to check the result of each SQL statement (to support conditional logic)
				$Globals::ENV{PRESCAN}->{BTEQ_MODE} ? $sql_wrapper_template = $CFG_POINTER->{xsql_dql_wrapper} 
				                           : $sql_wrapper_template = $CFG_POINTER->{sparksql_wrapper};
			} 
			else
			{
				# $sql_wrapper_template = $CFG_POINTER->{xsql_dml_wrapper};

				# BTEQ_MODE means we need to check the result of each SQL statement (to support conditional logic)
				$Globals::ENV{PRESCAN}->{BTEQ_MODE} ? $sql_wrapper_template = $CFG_POINTER->{xsql_dml_wrapper} 
				                           : $sql_wrapper_template = $CFG_POINTER->{sparksql_wrapper};
			}
			$sql_wrapper_template =~ s{%SQL%}{$sql};
			$sql = $sql_wrapper_template;

			# Original SQL comments inside a SQL wrapper need to stay as "--"
			$sql =~ s{^(\s*\-\-.*)}{$1<:sql_comment:>}mg;
		}
	}

	# If we have a GOTO <label> 
	#    save the label in $CFG_POINTER->{GOTO_LABEL} or somewhere globally
	#    DO NOT add the $nb_command
	# If we have a label and it matches the saved GOTO label (always should, because of not supporting oiverlapping GOTO / LABEL
	#    delete $CFG_POINTER->{GOTO_LABEL}
	#    DO NOT add the $nb_command
	if ($sql =~ m{^\-\-<indent\+\+>\s*GOTO\s*([^\s;]+)}mi)
	{
		$CFG_POINTER->{GOTO_LABEL} = $1;
		# return $sql;
	}
	elsif ($sql =~ m{^\-\-<indent=0>\s*([^\s;]+)}mi)
	{
		my $label = $1;
		if ($CFG_POINTER->{GOTO_LABEL} eq $label)
		{
			delete($CFG_POINTER->{GOTO_LABEL});
			return $sql;
		}
	}
	elsif ($CFG_POINTER->{GOTO_LABEL})
	{
		return $sql;
	}

	return $sql if (is_all_comments_or_blanks($sql));

	# $sql = "\n\n$nb_COMMAND\n$sql" if $CFG_POINTER->{use_notebook_md};
	if ($CFG_POINTER->{use_notebook_md})
	{
		if ($Globals::ENV{PRESCAN}->{use_sql_statement_wrapper})
		{
			$sql = "\n\n$nb_COMMAND_python\n$sql";
		}
		else
		{
			$sql = "\n\n$nb_COMMAND_sql\n$sql";
		}
	}

	return $sql;
}

sub adjust_multiline_comment
{
	my $comment = shift;
	while ($comment =~ /(\/\*(.*?)\*\/)/gis)
	{
		my ($prematch, $match, $postmatch) = (${^PREMATCH}, ${^MATCH}, ${^POSTMATCH});
		$MR->log_msg("adjust_multiline_comment\nPRE: $prematch\nMATCH: $match\nPOST: $postmatch");
		$match =~ s/\/\*/--/gis;
		$match =~ s/\*\//--/gis;
		$match =~ s/\n/\n--/gis;
		$MR->log_msg("adjust_multiline_comment: MATCH AFTER: $match");
		$comment = $prematch . $match . $postmatch;
		#$comment = 'MULT LINE';
	}
	return $comment;
}

sub hide 
# In the provided text, convert each instance of anything that matches a provided pattern to a unique string,
# saving the unique string in a hash (for "unhiding" later), returning the modified text
{
	my $text = shift;
	my $pattern = shift;
	my $marker = shift;
	my $unique = $marker . $hide_num++ . $marker;
	while ($text =~ s{($pattern)}{$unique} ) 
	{
		$hide_hash{$unique} = $1;
		$unique = $marker . $hide_num++ . $marker;
	}
	return $text;
}

sub unhide 
# Convert "hidden" things back to their original state
{
	my $text = shift;
	my $marker = shift;
	$text =~ s{$marker(\d+)$marker}{$hide_hash{"$marker$1$marker"}}gs;
	return $text;
}

sub databricks_create_table_as_text_format
# Called from config
{
	my $cont = shift;
	my $create_table_as_text_attribs = shift @{$Globals::ENV{PRESCAN}->{CREATE_TABLE_AS_TEXT_ATTRIBS}};
	my $table_attribs_output = '';

	$cont =~ s{__CREATE_TABLE_AS_TEXT_ATTRIBS__}{};

	# If set to "1", do not convert text table formats to "DELTA" in "CREATE TABLE"
	# "retain_text_table_formats": "1",
	if ($CFG_POINTER->{retain_text_table_formats})
	{
		if ($cont =~ m{\bEXTERNAL\s+TABLE\b}i)
		{
			$cont = "--<:fixme:> databricks.migrations.task update table location\n$cont";
		}
	}
	else
	{
		$table_attribs_output = "using delta\n";
	}

	return $cont . $table_attribs_output . ";\n";
}

sub databricks_load_data_into_table_sql
{
	my $file_import = shift @{$Globals::ENV{PRESCAN}->{FILE_IMPORT}};

	my $table_name  = $file_import->{TABLE_NAME}; 
	my $inpath      = $file_import->{INPATH}; 
	my $delim       = $file_import->{DELIMITER}; 
	my $skip_header = $file_import->{SKIP_HEADER}; 
	my $output = "";
	my $header_spec = $skip_header?"\,\n'header' = 'true'":"";

	my $output = "COPY INTO $table_name
  FROM $inpath
  FILEFORMAT = \'CSV\'
  FORMAT_OPTIONS (
    'delimiter'='$delim',
     'inferSchema'='true'$header_spec
  )";

  $output = convert_dml($output);  # Make sure code goes through SQL conversion

  return $output;
}

sub databricks_insert_overwrite_table
{
	my $cont = shift;

	# $MR->log_error(Dumper($Globals::ENV{PRESCAN}));

	# Prevents false matches	
	return $cont if ( ! $Globals::ENV{PRESCAN}->{INSERT_OVERWRITE_TABLE});

	my $insert_overwrite_table_info = shift @{$Globals::ENV{PRESCAN}->{INSERT_OVERWRITE_TABLE}};

	my $partition_cols = $insert_overwrite_table_info->{PARTITION_COLS};

	# This will be set to 'multi' or 'single'
	my $partition_col_value_type = '';

	# Get separate static and dynamic partition copls into separate arrays
	my @static_partition_cols = ();
	my @dynamic_partition_cols = ();
	foreach my $partition_col (@{$partition_cols})
	{
		if ($partition_col->{type} eq 'static')
		{
			push(@static_partition_cols, $partition_col->{name});
		}
		else
		{
			push(@dynamic_partition_cols, $partition_col->{name});
			$partition_col_value_type = $partition_col->{value_type};
		}
	}
	my $output = '';
	my $sql = '';

	# If there are no dynamic partition cols, e.g. "PARTITION (x = 1, y = 2)", then no conversion is required
	if ( ! @dynamic_partition_cols)
	{
		$sql = $insert_overwrite_table_info->{WHOLE_INSERT};
		$sql =~ s{\binsert\s+overwrite\s+table\s}{<<<:INSERT_OVERWRITE_TABLE:>>>}i;
		$sql = convert_dml($sql);
		$output = $insert_overwrite_table_info->{BEFORE_INSERT}
				. $sql;
		return $output;
	}

	# If we have both dynamic and static partition cols then report and do not convert
	if (@dynamic_partition_cols and @static_partition_cols)
	{
		$sql = $insert_overwrite_table_info->{WHOLE_INSERT};
		$sql =~ s{\binsert\s+overwrite\s+table\s}{<<<:INSERT_OVERWRITE_TABLE:>>>}i;
		$sql = convert_dml($sql);
		$output = $insert_overwrite_table_info->{BEFORE_INSERT}
				. $sql;
		return "--<:fixme:> databricks.migrations.unsupported.feature partition overwrite with both static and dynamic partition columns\n"
				. $output;
	}

	# If we are here then we have only dynamic partition columns, so we need to convert to static

	# For multi-value partition cols, i.e. where the partition col is variable, i.e. variable values from the SELECT,
	# we need to generate regular SQL code (as opposed to spark.sql code)
	if ($CFG_POINTER->{force_delete_insert_for_single_partition_columns} or $partition_col_value_type eq 'multi'
	or $insert_overwrite_table_info->{SELECT_COLS}[$#{$insert_overwrite_table_info->{SELECT_COLS}}]  # Check LAST select col for CURRENT_DATE 
																  =~ m{\([^()]*\bcurrent_date\b}si)  # being used in a function, i.e. in parens
	{

		$sql = $insert_overwrite_table_info->{BEFORE_INSERT};
		$output =  $sql . "\n";

		# Get the SELECT cols that correspond to the partition cols, e.g. for "PARTITION(a, b)" get the last TWO SELECT cols,
		# or for "PARTITION(colx)" get the last SELECT col
		my @partition_static_cols = @{$insert_overwrite_table_info->{SELECT_COLS}}    # Take elements from this array
								 [ $#{$insert_overwrite_table_info->{SELECT_COLS}}    # starting at number-of-partition-cols
								   - $#dynamic_partition_cols                         #                        from the end 
								 ..$#{$insert_overwrite_table_info->{SELECT_COLS}} ]; # through to the end

		# Delete the partition. If the original SELECT is "*", then we need to do "DELETE...WHERE...IN...<partition_col>",
		# otherwise we will do "DELETE...WHERE...IN...<select_col>"
		my $in_select = '';
		if ($partition_static_cols[0] =~ m{^\s*\*\s*$})  #this does not activate when it should, maybe make a config override?
		{
			$in_select = "select $dynamic_partition_cols[0]";   # Use the col name from the PARTITION(...)
		}
		else
		{
			$in_select = "select $partition_static_cols[0]";    # Use the col name from the original SELECT
		}

		$sql = "DELETE FROM $insert_overwrite_table_info->{TABLE_NAME}\nWHERE "
			 . "$dynamic_partition_cols[0] in (\n"
			 # . "select $partition_static_cols[0]\n"
			 . "$in_select\n";

		my $insert_from_statement = $Globals::ENV{PRESCAN}->{INSERT_FROM_CLAUSES}->{$insert_overwrite_table_info->{FROM_TABLE}};

		if ($insert_from_statement && $CFG_POINTER->{use_prescan_insert_from_clauses})
		{
			my $insert = "\n(";
			$insert = $insert_overwrite_table_info->{FROM_TABLE} if $insert_overwrite_table_info->{FROM_TABLE};
			$sql .= "FROM $insert\n$insert_from_statement);\n";
		}
		else
		{
			$sql .= "FROM $insert_overwrite_table_info->{FROM_TABLE});\n";
		}

		if ($CFG_POINTER->{use_distinct_column_in_delete_from_clauses})
		{
			$sql =~ s/distinct \*/distinct $dynamic_partition_cols[0]/gis;
		}

		$sql = convert_dml($sql);  # Make sure code goes through SQL conversion
		$output .= $sql;

		my $from = '';
		if ($insert_overwrite_table_info->{FROM_SUBQUERY})
		{
			$from = 'FROM (';
		}
		else
		{
			$from = "FROM $insert_overwrite_table_info->{FROM_TABLE}";
		}

		$output .= "\n-- COMMAND ----------\n";

		$sql = "INSERT INTO TABLE $insert_overwrite_table_info->{TABLE_NAME} PARTITION ($dynamic_partition_cols[0])\n"
			 . "SELECT\n"
			 . join(",\n", @{$insert_overwrite_table_info->{SELECT_COLS}})
			 # . "\nFROM $insert_overwrite_table_info->{FROM_TABLE}\n"
			 . "\n$from\n"
			 . "$insert_overwrite_table_info->{FROM_CLAUSE};\n";
		$sql = convert_dml($sql);  # Make sure code goes through SQL conversion
		$output .= $sql;
	}

	# For single-value partition cols, i.e. where the value in the SELECT is constant, we need to generate spark.sql code
	else
	{
		my $before_insert = $insert_overwrite_table_info->{BEFORE_INSERT};
		# $before_insert = convert_sql_comments_to_python($before_insert);
		$output = $before_insert . "\n";

		my $spark_sql = '';
		my @partition_static_cols = @{$insert_overwrite_table_info->{SELECT_COLS}}    # Take elements from this array
								 [ $#{$insert_overwrite_table_info->{SELECT_COLS}}    # starting at number-of-partition-cols
								   - $#dynamic_partition_cols                         #                        from the end 
								 ..$#{$insert_overwrite_table_info->{SELECT_COLS}} ]; # through to the end
		$output = "%python\nspark.sql(\"\"\"\n$output";
		$output .= "     <<<:INSERT_OVERWRITE_TABLE:>>> $insert_overwrite_table_info->{TABLE_NAME} PARTITION (\n";

		my $col_num = 0;
		my @spark_sql_format = ();
		foreach (@dynamic_partition_cols)
		{
			# Create an entry like <col_name>_val = p.col<col_num> in an array to use in the spark.sql .format
			$col_num++;
			push(@spark_sql_format, $_ . '_val = spark.sql("values ' . $partition_static_cols[$col_num -1] . '").collect()[0].col' . $col_num );

			# Change the array entry from: <col_name> to: <col_name> = '{<col_name>_val}'
			$_ .= " = '{" . $_ . "_val}'";
		}

		# The select cols that correspond to the partition cols need to be removed (from the select cols)
		splice(@{$insert_overwrite_table_info->{SELECT_COLS}}, scalar(@dynamic_partition_cols) * -1);

		$output .= join(",\n        ", @dynamic_partition_cols)
				. "\n     )\n";
		$spark_sql = "     SELECT\n"
				   . join(",\n        ", @{$insert_overwrite_table_info->{SELECT_COLS}})
				   . "\n     FROM $insert_overwrite_table_info->{FROM_TABLE}\n"
				   . "\n     $insert_overwrite_table_info->{FROM_CLAUSE};\n";
		$spark_sql = convert_dml($spark_sql);  # Make sure code goes through SQL conversion

		$output .= $spark_sql		
				. "   \"\"\").format(\n";

		$output .= join(",", @spark_sql_format)
				. "\n).display();\n";

	}
	return $output;

}

sub insert_overwrite_sql 
{
	my $text = shift; 
	$MR->log_msg("STARTING INSERT OVERWRITE  $text");

	$text =~ /insert\s*overwrite\s*table\s*(.*?)\s*partition\s*\((.*?)\)\s*select\s*(.*?)\s+from\s+(.*)/gis;
	my $tblname =  $1;
	my $partitioned_column =  $2; 
	my $all_cols =  $3;
	#my $last_column =  $MR->trim($4);
	my $rest =  $4 ;

	my @arg = $MR->get_direct_function_args($all_cols);

	my $last_column = $arg[$#arg];
	$all_cols = join("\n,", @arg[0..$#arg-1]);
	$MR->log_msg("INSERT OVERWRITE SQL ARGS:  " . Dumper(@arg));
	if($last_column =~ /current_date/gis)
	{
		my $additional_widget = $CFG_POINTER->{VAR_DECL};
		 $additional_widget =~ s/%NAME%/current_date_val/gis;
		 #$additional_widget =~ s/ \"A\"/current_date_widget/gis;

		$ENV{WIDGET} .= "\n$additional_widget";
		$last_column = "\$current_date_val";

	}

	$MR->log_msg("ELEMENTS table : $tblname \n partitioned_column: $partitioned_column \nall columns:$all_cols\n last column :$last_column \n rest : $rest");

	#Perform static insertion 
	if($last_column =~ /getArgument/gis || $last_column =~ /\$/gis )
	{
		$last_column =~ s/(.*?)\s*as\s*.*/$1/gis;
		$MR->log_msg("last column vv : $last_column");
		$last_column =~ s/\'\$\{hivevar\:(.*?)\}\'/\$$1/gis;
		$last_column =~ s/\'\$\{(.*?)\}\'/\$$1/gis;
		$last_column =~ s/\w+\((.*?)\)/$1/gis;
	
	my $output = "INSERT OVERWRITE TABLE $tblname partition($partitioned_column = $last_column)
	select $all_cols
	from $rest ";
	return $output if ($output =~ /\;/gis);
	return $output . ";"; 
	}

	return "--NON STATIC INSERTION \n$text";

}


sub replace_params_as_spark
{
	my $sql = shift; 

	$MR->log_msg("STARTING REPLACE PARAM FOR SPARK"); 
	if($sql =~ /{(\w+)}/)
	{
		my $table_name = $1;
		$sql =~ /(spark.sql\(.*)\"\"\"(.*)/gis;
		$sql = $1 . "\"\"\".format($table_name)$2";

	}
	return $sql; 
}

sub select_into_variable
{
	my $ar = shift;
    
	my $str = join("\n", @$ar);
	if ($str =~/.*?(\bSELECT\b\s+)into\b\s+(\w+)\s+\*(\s+\bFROM\b.*\;)/gis){
		$str= $1." * INTO ".$2." ".$3;
	}
	$str =~/.*?(\bSELECT\b.*?\binto\b\s+(.*?)\bFROM\b.*\;)/gis;
	$MR->log_msg("entering select into $str"); 
    $str = $1;	
	my $columns = $MR->trim($2);
	my @vars = split(/\,/,$columns);
	$str = wrap_args($str);
	my %var_hash = map{$_->{NAME} => 1} @{$Globals::ENV{PRESCAN}->{VARIABLES}};
	
	my $ret_str = '';
    my $tab_tag = $CFG_POINTER->{tab_tag};
	$tab_tag =~ s/\%count\%/$PHYTON_SCOPE_LEVEL/gis;
	my $begin_tag = get_begin_tag();
	$ret_str =~ s/\bbegin\b/begin_$BEGIN_LEVEL/gis;
	if ($vars[0] ne '*')
	{
		$str = "$str";
		
		$str =~ s/(\bSELECT\b.*?)\bINTO\b\s+.*?\bFROM\b/$1\nFROM/gis;
		$str = $MR->trim($str);
		my $select_into_query = $CFG_POINTER->{commands}->{SELECT_INTO_QUERY};
		$select_into_query =~ s/\%COLUMNS\%/$columns/gis;
		$select_into_query =~ s/\%QUERY\%/$str/gis;
        
		foreach my $v (@vars)
		{
			$v= $MR->trim($v);
			my $select_into_set = $CFG_POINTER->{commands}->{SELECT_INTO_SET};
			$select_into_set =~ s/\%VARIABLE\%/$v/gis;
			$select_into_query .= $PREFIX_TAG.$tab_tag.$select_into_set;
		}
		$ret_str.= $select_into_query;
    }
	else
	{
		$ret_str = $CFG_POINTER->{commands}->{SWAP};
		$ret_str =~ s/\%QUERY\%/$str/gis;
	}
	
	$ret_str = $sql_parser->convert_sql_fragment($PREFIX_TAG.$tab_tag.$ret_str);
	
	return $ret_str;
}

#this sub inserts unused columns into INSERT(..) SELECT clauses, because Databricks does not automatically handle NULL column inserts
sub insert_with_select
{
	my $ar = shift;
	if (!$CFG_POINTER->{use_catalog})
	{
        return;
    }
    
	my $str = join("\n", @$ar);
	$MR->log_msg("Entering insert_with_select: $str");
	my $missed_insert_columns = '';
	my $missed_select_columns = '';
	if ($str =~ /\s+(\w+\.?\w*\.?\w*)\s*\((.*)\)\s*\(?\s*SELECT\b/gis)
	{
        my $table_name = uc($1);
        my @insert_columns = split(/\,/, uc($2));
		my %hashed_insert_columns = map {$MR->trim($_) => 1} @insert_columns;
		if (!$CATALOG->{$table_name})
		{
            return $str;
        }
        
		foreach my $col (keys %{$CATALOG->{$table_name}})
		{
			$col = $MR->trim($col);
			if (!$hashed_insert_columns{$col})
			{
				$missed_insert_columns .= ", $col\n";
				$missed_select_columns .= ", null as $col\n";
            }
		}
		$str =~ s/(.*)\((.*)\)(\s*\(?\s*SELECT\b.*?)\bFROM\b(\s*\(\s*select)/$1($2$missed_insert_columns)$3$missed_select_columns FROM$4/gis;
		$str =~ s/(.*)\((.*)\)(\s*\(?\s*SELECT\b.*?)\bFROM\b(\s+\w*\.*\w+\s*\;)/$1($2$missed_insert_columns)$3$missed_select_columns FROM$4/gis;
		$str =~ s/(.*)\((.*)\)(\s*\(?\s*SELECT\b.*?)\bFROM\b(\s+\w*\.*\w+\s+\w+\s*\;)/$1($2$missed_insert_columns)$3$missed_select_columns FROM$4/gis;
		$str =~ s/(.*)\((.*)\)(\s*\(?\s*SELECT\b.*?)\bFROM\b(\s+\w*\.*\w+\s+\w+\s+where)/$1($2$missed_insert_columns)$3$missed_select_columns FROM$4/gis;
		$str =~ s/(.*)\((.*)\)(\s*\(?\s*SELECT\b.*?)\bFROM\b(\s+\w*\.*\w+\s+\w+\s+\w+\s+JOIN)/$1($2$missed_insert_columns)$3$missed_select_columns FROM$4/gis;
		$str =~ s/(\bUNION\b.*?\s*SELECT\b.*?)\bFROM\b(\s*\(\s*select)/$1$3$missed_select_columns FROM$4/gis;
		$str =~ s/(\bUNION\b.*?\s*SELECT\b.*?)\bFROM\b(\s+\w*\.*\w+\s*\;)/$1$3$missed_select_columns FROM$4/gis;
		$str =~ s/(\bUNION\b.*?\s*SELECT\b.*?)\bFROM\b(\s+\w*\.*\w+\s+\w+\s*\;)/$1$3$missed_select_columns FROM$4/gis;
		$str =~ s/(\bUNION\b.*?\s*SELECT\b.*?)\bFROM\b(\s+\w*\.*\w+\s+\w+\s+where)/$1$3$missed_select_columns FROM$4/gis;
		$str =~ s/(\bUNION\b.*?\s*SELECT\b.*?)\bFROM\b(\s+\w*\.*\w+\s+\w+\s+\w+\s+JOIN)/$1$3$missed_select_columns FROM$4/gis;
    }
    $str = $CONVERTER->convert_sql_fragment($MR->trim($str));
	$MR->log_msg("Output insert_with_select: $str");
	return $str;
}

sub fill_catalog_file
{
	my $path = shift;
	my @cont = $MR->read_file_content_as_array($path);
	foreach my $ln (@cont) #iterate through lines
	{
		my @table_cont = split(/\|/, $ln);
		$CATALOG->{uc($MR->trim($table_cont[0]))}->{uc($MR->trim($table_cont[1]))} = 1;
	}
	$MR->debug_msg("Catalog File: " . Dumper($CATALOG));
}


sub loop_start
{
	my $ar = shift;
	my $script = join("\n", @$ar);
	$MR->log_msg("loop_start: $script");
	$script = $MR->trim($script);
	my $tab_tag = $CFG_POINTER->{tab_tag};
	$tab_tag =~ s/\%count\%/$PHYTON_SCOPE_LEVEL/gis;
	my $begin_tag = get_begin_tag();
	
	$script = $sql_parser->convert_sql_fragment($PREFIX_TAG.$tab_tag.$script);
	$PHYTON_SCOPE_LEVEL += 1;
	return $script;
}

sub loop_end
{
	my $ar = shift;
	my $script = join("\n", @$ar);
	$MR->log_msg("loop_end: $script");
	$script = $MR->trim($script);
	$PHYTON_SCOPE_LEVEL -= 1;
	my $tab_tag = $CFG_POINTER->{tab_tag};
	$tab_tag =~ s/\%count\%/$PHYTON_SCOPE_LEVEL/gis;
	my $begin_tag = get_begin_tag();
	$script = $sql_parser->convert_sql_fragment($PREFIX_TAG.$tab_tag.$script);
	return $script;
}

sub if_start
{
	my $ar = shift;
	my $script = join("\n", @$ar);
	$MR->log_msg("if_start: $script");
	$script = $MR->trim($script);
	my $tab_tag = $CFG_POINTER->{tab_tag};
	$tab_tag =~ s/\%count\%/$PHYTON_SCOPE_LEVEL/gis;
	
	#my $begin_tag = get_begin_tag();
	
	$script = $sql_parser->convert_sql_fragment($PREFIX_TAG.$tab_tag.$script);
	$PHYTON_SCOPE_LEVEL += 1;
	return $script;
}
sub elif_start
{
	my $ar = shift;
	my $script = join("\n", @$ar);
	$MR->log_msg("if_start: $script");
	$script = $MR->trim($script);
	$PHYTON_SCOPE_LEVEL -= 1;
	my $tab_tag = $CFG_POINTER->{tab_tag};
	$tab_tag =~ s/\%count\%/$PHYTON_SCOPE_LEVEL/gis;
	
	#my $begin_tag = get_begin_tag();
	
	$script = $sql_parser->convert_sql_fragment($PREFIX_TAG.$tab_tag.$script);
	$PHYTON_SCOPE_LEVEL += 1;
	return $script;
}
sub elsif_start
{
	my $ar = shift;
	my $script = join("\n", @$ar);
    $MR->log_msg("elif_start: $PHYTON_SCOPE_LEVEL");
	$script = $MR->trim($script);
	#$PHYTON_SCOPE_LEVEL -= 1;
	$PHYTON_SCOPE_LEVEL += 3;
    $MR->log_msg("elif_start: $script");
	
	my $tab_tag = $CFG_POINTER->{tab_tag};
	$tab_tag =~ s/\%count\%/$PHYTON_SCOPE_LEVEL/gis;
	
	#my $begin_tag = get_begin_tag();
	#$MR->log_msg("elif_start: $PHYTON_SCOPE_LEVEL");
	
	$script = $sql_parser->convert_sql_fragment($PREFIX_TAG.$tab_tag.$script);
	$MR->log_msg("elif_start: $PHYTON_SCOPE_LEVEL");
	
	return $script;
}

sub if_end
{
	my $ar = shift;
	my $script = join("\n", @$ar);
	$MR->log_msg("if_end: $script");
	$script = $MR->trim($script);

	my $tab_tag = $CFG_POINTER->{tab_tag};
	$tab_tag =~ s/\%count\%/$PHYTON_SCOPE_LEVEL/gis;
	
	my $begin_tag = get_begin_tag();
	
	$script = $sql_parser->convert_sql_fragment($PREFIX_TAG.$tab_tag.$script);
	$PHYTON_SCOPE_LEVEL -= 1;
	return $script;
}

sub while_start
{
	my $ar = shift;
	my $script = join("\n", @$ar);
	$MR->log_msg("while_start: $script");
	$script = $MR->trim($script);
	my $tab_tag = $CFG_POINTER->{tab_tag};
	$tab_tag =~ s/\%count\%/$PHYTON_SCOPE_LEVEL/gis;
	
	my $begin_tag = get_begin_tag();
	
	$script = $sql_parser->convert_sql_fragment($PREFIX_TAG.$tab_tag.$script);
	$PHYTON_SCOPE_LEVEL += 1;
	return $script;
}

sub while_end
{
	my $ar = shift;
	my $script = join("\n", @$ar);
	$MR->log_msg("while_end: $script");
	$script = $MR->trim($script);
	
	$PHYTON_SCOPE_LEVEL -= 1;
	my $tab_tag = $CFG_POINTER->{tab_tag};
	$tab_tag =~ s/\%count\%/$PHYTON_SCOPE_LEVEL/gis;
	
	my $begin_tag = get_begin_tag();
	
	$script = $sql_parser->convert_sql_fragment($PREFIX_TAG.$tab_tag.$script);
	return $script;
}

sub for_start
{
	my $ar = shift;
	my $script = join("\n", @$ar);
	$MR->log_msg("for_start: $script");
	$script = $MR->trim($script);
	my $tab_tag = $CFG_POINTER->{tab_tag};
	$tab_tag =~ s/\%count\%/$PHYTON_SCOPE_LEVEL/gis;
	
	my $begin_tag = get_begin_tag();
	
	$script = $sql_parser->convert_sql_fragment($PREFIX_TAG.$tab_tag.$script);
	$PHYTON_SCOPE_LEVEL += 1;
	return $script;
}

sub exception_start
{
	my $ar = shift;
	my $script = join("\n", @$ar);
	$MR->log_msg("exception_start: $script");
	$script = $MR->trim($script);

	my $tab_tag = $CFG_POINTER->{tab_tag};
	
	if ($PHYTON_SCOPE_LEVEL - 1 >=0){
    $PHYTON_SCOPE_LEVEL -= 1;
 	$BEGIN_LEVEL -= 1;
	}
	$tab_tag =~ s/\%count\%/$PHYTON_SCOPE_LEVEL/gis;
	my $begin_tag = get_begin_tag();
	$script =~ s/\bbegin\b/begin_$BEGIN_LEVEL/gis;
	$script = $sql_parser->convert_sql_fragment($PREFIX_TAG.$tab_tag.$script);

		
	
	$PHYTON_SCOPE_LEVEL += 1;
 	$BEGIN_LEVEL += 1;
	
    
	return $script;
}

sub exception_end
{
	my $ar = shift;
	my $script = join("\n", @$ar);
	$script = $MR->trim($script);
	
	my $tab_tag = $CFG_POINTER->{tab_tag};
	$tab_tag =~ s/\%count\%/$PHYTON_SCOPE_LEVEL/gis;
	my $begin_tag = get_begin_tag();
	$script =~ s/\bend_empty\b/end_$BEGIN_LEVEL/gis;
	#$PHYTON_SCOPE_LEVEL -= 1;
	#$BEGIN_LEVEL -= 1;
	if ($PHYTON_SCOPE_LEVEL - 1 ==0){
    $PHYTON_SCOPE_LEVEL -= 1;
 	$BEGIN_LEVEL -= 1;
	}
	$script = $sql_parser->convert_sql_fragment($PREFIX_TAG.$tab_tag.$script);
	
	
	#$script=~s//gis;
	return $script;
}




sub begin_start
{
	my $ar = shift;
	my $script = join("\n", @$ar);
	
	$MR->log_msg("begin_start: $script");
	$script = $MR->trim($script);

	my $tab_tag = $CFG_POINTER->{tab_tag};
	$tab_tag =~ s/\%count\%/$PHYTON_SCOPE_LEVEL/gis;

	my $begin_tag = get_begin_tag();
	$script =~ s/\bbegin\b/begin_$BEGIN_LEVEL/gis;
	$MR->log_msg("begin_start------------------------------------: $tab_tag");
	$script = $sql_parser->convert_sql_fragment($PREFIX_TAG.$tab_tag.$script);
	
	
	$PHYTON_SCOPE_LEVEL += 1;
	$BEGIN_LEVEL += 1;
    $MR->log_msg("begin_start------------------------------------: $script");
	return $script;
}

sub begin_end
{
	my $ar = shift;
	my $script = join("\n", @$ar);
	$script = $MR->trim($script);
	
	my $tab_tag = $CFG_POINTER->{tab_tag};
	$tab_tag =~ s/\%count\%/$PHYTON_SCOPE_LEVEL/gis;
	my $begin_tag = get_begin_tag();
	$script =~ s/\bend_empty\b/end_$BEGIN_LEVEL/gis;
	if ($PHYTON_SCOPE_LEVEL > 0)
	{
	    $PHYTON_SCOPE_LEVEL -= 1;
	 	$BEGIN_LEVEL -= 1;
	}
	$script = $sql_parser->convert_sql_fragment($PREFIX_TAG.$tab_tag.$script);
	return $script;
}

sub comment_handler
{
	my $ar = shift;
	my $cont = join("\n", @$ar);
	$MR->log_msg("comment_handler: $cont");

	if($IS_PYTHON_SCRIPT)
	{
		$cont =~ s/^\s*\-\-(.*);/#$1/g;
	}
	else
	{
		$cont =~ s/^\s*\-\-(.*);/--$1/g;
	}

	return $cont;
}

sub check_if_script_contains_python_elements
{
	my $script = shift;
	my $is_full_script = shift;
	
	if($CFG_POINTER->{always_python})
	{
		return 1;
	}
    
	if($is_full_script)
	{
		foreach my $regex (@{$CFG_POINTER->{set_global_python_keys}})
		{
			if ($script =~ /$regex/gis)
			{
				$is_exception = 1;
				return $is_exception;
			}
		}
    }
	
    if ($is_exception)
	{
        return 1;
    }
    
	foreach my $regex (@{$CFG_POINTER->{python_keys_regex}})
	{
		if ($script =~ /$regex/gis)
		{
            return 1;
        }
	}
	return 0;
}


sub get_begin_tag
{
	my $begin_tag = '';
	
	if ($BEGIN_LEVEL > 1)
	{		
		$begin_tag = $CFG_POINTER->{begin_tag};
		$begin_tag =~ s/\%level\%/$BEGIN_LEVEL/gis;
    }
	
	return $begin_tag;
}

sub value_columns
{
	my $ar = shift;
	my $script = join("\n", @$ar);
	$MR->log_msg("value_columns: $script");
	my $tab_tag = $CFG_POINTER->{tab_tag};
	$tab_tag =~ s/\%count\%/$PHYTON_SCOPE_LEVEL/gis;
	my $begin_tag = get_begin_tag();
	$script = $MR->trim($script);
	$script = $sql_parser->convert_sql_fragment($PREFIX_TAG.$tab_tag.$script);
	$script =~ s/\w+\s+as\b/col1 as/gis; 
	$MR->log_msg("values_values: script");
	
	if ($is_exception or $IS_SCRIPT)
	{
			$script =$PREFIX_TAG.$tab_tag.$script;
	}
	$script = $sql_parser->convert_sql_fragment($script);
	#$script = wrap_args($script)
	return $script;
}
sub insert_all
{
	my $ar = shift;
	my $script = join("\n", @$ar);
	$MR->log_msg("insert_all: $script");
	my $tab_tag = $CFG_POINTER->{tab_tag};
	$tab_tag =~ s/\%count\%/$PHYTON_SCOPE_LEVEL/gis;
	my $begin_tag = get_begin_tag();
	$script = $MR->trim($script);
	$script =~ s/into/INTO/gis;
	if ($script =~ /(insert\s+all\s+)(into.*?)(select.*?)\;/gis)
	{ 
		my $inst_stmt = $2;
		
		my @rt_ar = split("INTO", $inst_stmt);
		my @rt_ar2;
		foreach my $into (@rt_ar)
		{
			if ($into ne '')
			{
			if ($is_exception or $IS_SCRIPT)
			{
		        push(@rt_ar2, $PREFIX_TAG.$tab_tag.'spark.sql(f"""INSERT INTO'.$into.$MR->trim($3).'""")'."\n");
			}
		
			else
			{			
			push(@rt_ar2, "INSERT INTO ".$into.$3.";\n");
			}		
		}
		}
		my $ret_script = join("\n", @rt_ar2);
		
		
		$MR->log_msg("values_values: script");
		$ret_script = $sql_parser->convert_sql_fragment($ret_script);
		$script = wrap_args($script);
		return $ret_script;
	}
	#$script = $sql_parser->convert_sql_fragment($PREFIX_TAG.$tab_tag.$script);
	if ($script =~ /(insert\s+all\s+)(WHEN.*?)(ELSE\s+INTO\s+\w+)(\s+select.*?)\;/gis)
	{ 
		$script =~ s/WHEN/SPLIT WHEN/gis;
		$script =~ s/ELSE/SPLIT ELSE/gis;
		
	
		if($script =~ /(insert\s+all\s+)(SPLIT\s+WHEN.*?SPLIT\s+ELSE\s+INTO\s+\w+)(\s+select.*?)\;/gis){
			my $inst_stmt = $2;
			my $select = $3;
			my $else_cond ='';
			my @conditions;
			my @return;
			my @outer_ar = split("SPLIT", $inst_stmt);
			
			foreach my $when (@outer_ar){
				$MR->log_msg("when_values: $when");
				if($when =~/WHEN(.*?)THEN\s+(into.*)/gis){
					push(@conditions,$1);
					$MR->log_msg("when_values: $when");
					$when ="INSERT ".$MR->trim($2)."\n".$MR->trim($select)."\nwhere ".$1."\n";
					
					if ($is_exception or $IS_SCRIPT)
					{
						push(@return,$PREFIX_TAG.$tab_tag.'spark.sql(f"""'.$when.'""")');
					}
					else 
					{
						push(@return,$when.";");
					}
					
				}
				elsif($when =~ /ELSE(.*?)(into.*)/gis){
					foreach my $cond (@conditions){
						$else_cond = $else_cond. " not (".$cond. ")\nand " ; 
					} 
					$when ="INSERT ".$MR->trim($1)."\n".$MR->trim($select)."\nwhere ".$else_cond;
			
					if ($is_exception or $IS_SCRIPT)
					{
						push(@return,$PREFIX_TAG.$tab_tag.'spark.sql(f"""'.$when.';""")');
					}
					else
					{
						push(@return,$when.";");
			        }
			
			}
			}
			my $ret_script = join("\n", @return);
			$ret_script =~s/and\s*\;/;/gis; 
	   
		$ret_script = $sql_parser->convert_sql_fragment($ret_script);

		$script = wrap_args($script);
		return $ret_script;
		}
	}
	elsif($script =~ /(insert\s+all\s+)(WHEN.*?)(select.*?)\;/gis)
	{
	        my $inst_stmt = $2;
			my $select = $3;
			my $else_cond ='';
			my @return;
			my @outer_ar = split("WHEN", $inst_stmt);
			
			foreach my $when (@outer_ar){
				$MR->log_msg("when_values: $when");
				if($when =~/(.*?)THEN\s+(into.*)/gis){
					$MR->log_msg("when_values: $when");
					$when ="INSERT ".$MR->trim($2)."\n".$MR->trim($select)."\nwhere ".$1."\n";
					if ($is_exception or $IS_SCRIPT)
					{
						push(@return,$PREFIX_TAG.$tab_tag.'spark.sql(f"""'.$when.'""")');
					}
					else 
					{
						push(@return,$when.";");
					}
					
				}
			}
	    my $ret_script = join("\n", @return);
		
		$ret_script = $sql_parser->convert_sql_fragment($ret_script);

		return $ret_script;
	}	

   	if ($is_exception or $IS_SCRIPT)
	{
		$script =$PREFIX_TAG.$tab_tag.$script;
	}
	
	$script = $sql_parser->convert_sql_fragment($script);
    $script = wrap_args($script);
	return $script;
	
	}
	
sub insert_first
{
	my $ar = shift;
	my $script = join("\n", @$ar);
	
	my $tab_tag = $CFG_POINTER->{tab_tag};
	$tab_tag =~ s/\%count\%/$PHYTON_SCOPE_LEVEL/gis;
	my $begin_tag = get_begin_tag();
	#$script = $MR->trim($script);
	$script =~ s/WHEN/WHEN/gis;
	
	#$script = $sql_parser->convert_sql_fragment($PREFIX_TAG.$tab_tag.$script);
	if ($script =~ /(insert\s+first\s+)(WHEN.*?)(select.*?\bfrom\s+)(\w+)(.*)\;/gis)
	{ 
		$MR->log_msg("first_values: $2");
		my $inst_stmt = $2;
		my $select = $3.$4.$5;
		my $table =$4;
		my $sql_cond = $4.$5;
		my @conditions;
		my @return;
		my @outer_ar = split("WHEN", $inst_stmt);
	
		foreach my $when (@outer_ar){
			
			if($when =~/(.*?)THEN\s+into\s+(\w*\.*\w*\.*\w+)\s+values\s*\((.*?)\)/gis or $when =~/(.*?)THEN\s+into\s+(\w*\.*\w*\.*\w+)/gis )
			{
				my  $select_value_list = 'data.*';
				my $value_list = $3;
				if ($value_list ne ''){
                $select_value_list = $value_list;
				$select_value_list  =~ s/(\w+)/data.$1/gis;
				$value_list = "values(".$value_list.")";
                }
                					
				push(@conditions,"WHEN ".$1." THEN "."'".$MR->trim($2)."'");
				$MR->log_msg("when_values: $when");
				if ($is_exception or $IS_SCRIPT)
					{
					$when ="\n# DBTITLE 1,".$MR->trim($2)."\n".'spark.sql(f"""'."INSERT INTO ".$MR->trim($2)."\n".$value_list."\nSELECT ".$select_value_list."\nfrom ".$MR->trim($table)."_src"."\nwhere target ="."'".$MR->trim($2)."'".'""")'."\n";
                    $when = $PREFIX_TAG.$tab_tag.$when; 
					}
				else{					
					$when ="\n-- DBTITLE 1,".$MR->trim($2)."\n"."INSERT INTO ".$MR->trim($2)."\n".$value_list."\nSELECT ".$select_value_list."\nfrom ".$MR->trim($table)."_src"."\nwhere target ="."'".$MR->trim($2)."';\n";
				}	
			push(@return,$when);
				
			}
			
		}
			my $case = 'CREATE TEMPORARY VIEW '.$table."_src AS\nSELECT STRUCT(*) as data,\n CASE\n";
			my $condition_str = join("\n", @conditions);
			$MR->log_msg("insert_first: $condition_str");
			my $struct = $case.$condition_str."\nEND AS target\n from \n".$sql_cond."\;";
			if ($is_exception or $IS_SCRIPT)
			{
				$struct ='spark.sql(f"""'.$struct.'""")';
				$struct = $PREFIX_TAG.$tab_tag.$struct;
					
			}
					
			my $ret_script = join("\n", @return);
			$ret_script =  $struct."\n".$ret_script;
	        $script = wrap_args($script);
		    $ret_script = $sql_parser->convert_sql_fragment($ret_script);

             
			return $ret_script;
		}
	
	
   
   if ($is_exception or $IS_SCRIPT)
		{
			$script =$PREFIX_TAG.$tab_tag.$script;
		}
		$script = $sql_parser->convert_sql_fragment($script);

   $script = wrap_args($script);
   return $script;
}	

sub update_from
{
	my $ar = shift;
	my $script = join("\n", @$ar);
	$MR->log_msg("print_handler: $script");
	my $tab_tag = $CFG_POINTER->{tab_tag};
	$tab_tag =~ s/\%count\%/$PHYTON_SCOPE_LEVEL/gis;
	my $begin_tag = get_begin_tag();
    	if ($script =~ /\(\s*select.*?\)/gis){
		$script = $sql_parser->convert_sql_fragment($PREFIX_TAG.$tab_tag.$script);
		return $script;
	}
	$script = $MR->trim($script);
	#$script = $sql_parser->convert_sql_fragment($PREFIX_TAG.$tab_tag.$script);
	if ($script =~ /UPDATE\s+(\w*\.*\w*\.*\w+\s+\w*\s*)\bSET(\b.*?)\bFROM\s+(\w*\.*\w*\.*\w+\s+\w*\s*)where(.*?);/gis){
		$script =~ s/UPDATE\s+(\w*\.*\w*\.*\w+\s+\w*\s*)\bSET(\b.*?)\bFROM\s+(\w*\.*\w*\.*\w+\s+\w*\s*)where(.*?);/merge into $1 USING $3 on $4\nWHEN MATCHED THEN\nUPDATE SET $2/gis;
	}
	$script = wrap_args($script);
	$MR->log_msg("print_handler: script");
if (($is_exception or $IS_SCRIPT) and $SRC_TYPE ne 'SNOWFLAKE')
		{
			$script =$PREFIX_TAG.$tab_tag.'spark.sql(f"""'.$script.'""")';
		}
		
	$script = $sql_parser->convert_sql_fragment($PREFIX_TAG.$tab_tag.$script);
	return $script.";";
}

sub delete_from
{
	my $ar = shift;
	my $script = join("\n", @$ar);
	$MR->log_msg("delete_from: $script");
	my $tab_tag = $CFG_POINTER->{tab_tag};
	$tab_tag =~ s/\%count\%/$PHYTON_SCOPE_LEVEL/gis;
	my $begin_tag = get_begin_tag();
	$script = $MR->trim($script);
	#$script = $sql_parser->convert_sql_fragment($PREFIX_TAG.$tab_tag.$script);
	if ($script =~ /delete\s+from\s+(\w*\.*\w+)\s+(\w+)\s+(\w+)\s+where(.*?);/gis){
		$script =~ s/delete\s+from\s+(\w*\.*\w+)\s+(\w+)\s+(\w+)\s+where(.*?);/merge into $1 $2\nusing\n\t(select * from $3)\n on $4\nWHEN MATCHED THEN DELETE/gis;
	}
	$script = wrap_args($script);
	
	if (($is_exception or $IS_SCRIPT ) and $SRC_TYPE ne 'SNOWFLAKE')
		{
			$script =$PREFIX_TAG.$tab_tag.'spark.sql(f"""'.$script.'""")';
		}
		
	$script = $sql_parser->convert_sql_fragment($PREFIX_TAG.$tab_tag.$script);
	return $script.";";
}
	



sub search_all_folder {
    my ($folder) = @_;
	my @files ={};
	#$MR->log_msg("sub_folder_path $folder");
    if ( -d $folder ) {
        chdir $folder;
        opendir my $dh, $folder or die "can't open the directory: $!";
        while ( defined( my $file = readdir($dh) ) ) {
            #$MR->log_msg("sub_folder $file");
			chomp $file;
            next if $file eq '.' or $file eq '..';
			search_all_folder("$folder/$file"); 	
			
			if (-f $folder."/".$file) {
			#$MR->log_msg("sub_folder_path_file $folder/$file");
			push(@pkg_files,$folder."/".$file);	
			}
			#push(@files,$folder/$file);	
			#$MR->log_msg("sub_folder_path_file $folder/$file");
			
             ## recursive call
            
			#read_files($file) if ( -f $file );
			
        }
        closedir $dh or die "can't close directory: $!";
    }
#$MR->log_msg("sub_folder_path_file2 ".Dumper(@files));	
#return \@files;
}



	
	
sub read_file {
	my $ar =shift;
	my $script = $ar;#join("\n", @$ar);
	my $pkg_name;
	
	
	my @proc_name1 	= $script =~/procedure\s+(\w*\.*\w+).*?(\bIS\b|\bAS\b)/gis ;	
	$MR->log_msg("sub_folder_path_file2 ".Dumper(@proc_name1));	
	my @proc_name2  = $script =~/procedure\s+(\w*\.*\w+)\s*\;/gis;
	my @proc_name3 = (@proc_name1,@proc_name2);
	
	$script =~ s/(PACKAGE.*?\;\s*\/).*/$1/gis;
	
	
	
	#preprocess package vars
	$script =~s/(\w+)\s+EXCEPTION\s*\;/\nclass $1(Exception):\n\t\tpass/gis;
	my @comments = $script =~/(^\s*\/\*.*?\*\s*\/)/gims;
		
	for my $cm  (@comments)
	{
		if ($#comments > -1)
		{
			my $cm1 =$cm;	
			$cm1 =~ s/(^\s*\/\*)/\#$1/gis;
			$cm1 =~ s/(^\s*)/\#$1/gim;
		
			$script =~ s/\Q$cm\E/$cm1/gis;
		}
	}
	
	
	$script =~ s/(\;\s+)(^\s+\-\-)/$1#$2/gism;
	$script =~ s/(^\-\-)/#$1/gim;
	if($script =~ /CREATE\s+OR\s+REPLACE\s+PACKAGE\s+(\"*\w*\"*\.*\"*\w+\"*)/gis 
			or /.*CREATE\sPACKAGE\s+(\"*\w*\"*\.*\"*\w+\"*)/gis){
				 $pkg_name = $1;
				 $pkg_name =~s/\"//gis;
			}
	#$dirname = '.';
	my $cwd = getcwd();
	
	
	
	
	
	
	# my @funct_name = $script =~/(function\s+\w*\.*\w+\s*\.?*RETURN.*?\;)/gis ;
    
	my @funct_name  = $script =~/function\s+(\w*\.*\w+)\s*\(.*?RETURN.*?\;/gis ;	
	my @proc_name1 	= $script =~/procedure\s+(\w*\.*\w+).*?(\bIS\b|\bAS\b)/gis ;	
	$MR->log_msg("sub_folder_path_file2 ".Dumper(@proc_name1));	
	my @proc_name2  = $script =~/procedure\s+(\w*\.*\w+)\s*\;/gis;
	my @proc_name7  = $script =~/procedure\s+(\w*\.*\w+)\s*\(.*?\)\s*;/gis;
	my @proc_name = (@proc_name1,@proc_name2,@proc_name7);
	
	search_all_folder($SOURCE_FOLDER);
    chdir $cwd;
    my @files =@pkg_files;
	
	for my $function (@funct_name)
	{
		if ($#funct_name > -1)
		{
			foreach my $fn (@files)
			{
				my $fname = (split /\//, $fn)[-1];
				if($pkg_name.".".$MR->trim($function).".".$FILE_EXTENSION eq $MR->trim($fname) )
				{
					open(fh, '<', $fn);
					
					my $file_content = do { local $/; <fh> };
					$file_content = $file_content."\n".$pkg_name.".".$function." = classmethod(".$function.")\ndel globals()['".$function."']";
					$file_content = $file_content."\n#-- COMMAND ----------\n";
					$script =~ s/CREATE\s+function\s+$function\s*\(.*?RETURN.*?\;/$file_content/gis;
					$script =~ s/function\s+$function\s*\(.*?RETURN.*?\;/$file_content/gis;
				}
			}	
		}
	}
	# @files ={};
	for my $procedure (@proc_name)
	{
		if ($#proc_name > -1)
		{
			foreach my $fn (@files)
			{
				my $fname = (split /\//, $fn)[-1];
				if($pkg_name.".".$MR->trim($procedure).".".$FILE_EXTENSION eq $MR->trim($fname) )
				{
					open(fh, '<', $fn);
					my $file_content = do { local $/; <fh> };
					$file_content = $file_content."\n".$pkg_name.".".$procedure." = classmethod(".$procedure.")\ndel globals()['".$procedure."']";
					$file_content = $file_content."\n#-- COMMAND ----------\n";
				    $script =~ s/CREATE\s+procedure\s+$procedure\s*\(.*?\;/$file_content/gis;
					$script =~ s/procedure\s+$procedure\s*\;/$file_content/gis;
					$script =~ s/procedure\s+$procedure\s*\(.*?\;/$file_content/gis;
				}
			}	
		}
	}
	my @merged = (@proc_name, @funct_name);
	my %files = map { $_ => 1 } @merged;
	
	foreach my $fn (@files)
	{
				$MR->log_msg("mtliani ".Dumper($fn));
				my $fname = (split /\//, $fn)[-1];
				my $pkg_prefix = (split /\./, $fname)[-3];
				my $pkg_prefix_1 = (split /\./, $fname)[-4];
				#
				my $extracted_pkg='';
				if ($pkg_prefix_1 ne ''){
					$extracted_pkg = $pkg_prefix_1.".".$pkg_prefix;
					
				}
				else{
					$extracted_pkg=$pkg_prefix;
				}
				
				$fname = (split /\./, $fn)[-2];
				if(!$files{$fname}){
					$MR->log_msg("extracted_pkg equals ".$extracted_pkg);	
					if ($pkg_name eq $extracted_pkg){
					
					if($fname ne '')
					{
						open(fh, '<', $fn);
						my $file_content = do { local $/; <fh> };
						$file_content = $file_content."\n".$pkg_name.".".$fname." = classmethod(".$fname.")\ndel globals()['".$fname."']";
						$file_content = $file_content."\n#-- COMMAND ----------\n";
						$MR->log_msg("zaxruma $file_content");
						$script = $script."\n".$file_content;
						#$script =~ s/procedure\s+$fname\s*\(.*?\;/$file_content/gis;
					}
				}
	}
	#
	my @badparams = keys %files;
	$MR->log_msg("aris ".Dumper(@badparams));
	
	#
	}
	
	########################################################################################################
	# looks for variable declarations in spark.sql statments in functions and procedures and add format(var=pkg.var)
	my $format_str='';
	
	$script =~ s/(\w+\s+)CONSTANT(\s+.*?\:\=.*?\;)/$1$2/gis;
	
	$script =~ s/(\w+\s+)(\w+)\s*\(*\d+\)\s*(\:\=.*?\;)/$1 $2 $3/gis;
	
	
	my @dcl_var = $script=~/(\w+)\s+\w+\s*\:\=.*?\;/gis ;
	my @sprk_var = $script=~/(spark\.sql\s*\(\w*\"\"\".*?\"\"\"\))/gis ;
	
	for my $sprk (@sprk_var)
		{
			my $sprk1 = $sprk;
			if ($#sprk_var > -1)
			{
				for my $dr (@dcl_var)
				{
					if ($#dcl_var > -1)
					{
						if (index($sprk, $dr) != -1)
						#if ($sprk =~ /.*?$MR->trim($dr)/gis)
						{$MR->log_msg("aris_da_aris2 ".$dr);
							$format_str = $format_str.$dr."=pkg.".$dr.",";
							my $ss =$dr;
							$sprk1 =~ s/\Q$ss\E/{$ss}/gis;
							$MR->log_msg("aris_da_aris3 ".$sprk1);
						}
				
					}
				}
			}
		if($format_str ne ''){
		my $sprk2 = $sprk1.".format(".$format_str.")";	
		$sprk2 =~ s/\,\s*\)/)/gis;
		$script =~ s/\Q$sprk\E/$sprk2/;
		
		}
		$format_str='';
	}
	########################################################################################################

	# cursors with parameters  are changed to string and params are enclosed into {}
	my @crs_var = $script =~/(cursor\s+\w+\s*\((.*?)\)\s*is\s*(.*?)\;)/gis ; 
	if ($#crs_var > -1)
	{
		for my $cr (@crs_var){
		if($cr =~/(cursor\s+\w+\s*\((.*?)\)\s*is\s*(.*?)\;)/gis)	
		{
		my $cursor_args = $2;
		my $cursor_body = $3;
		my @cursor_args_def = split(',',$cursor_args);
		foreach my $crs_arg (@cursor_args_def){
			$crs_arg = $MR->trim($crs_arg);
			if($crs_arg =~ /(\w+)\s+\w+/is)
			{
				my $split_arg =$1;

				$cursor_body =~s/($split_arg)/{$1}/gis;
				
			}
		}
	
			
		
		
		$script =~s/(?<!\_DONE\_)cursor\s+(\w+)\s*\((.*?)\)\s*is\s*(.*?)\;/_DONE_$1 = """$cursor_body""";/is;
		}
		
	 }
	$script=~s/\s*\_DONE\_/\n/gis;
	}
   
   #############CHANGING PROC CALLS TO PKG>PROC_CALL and ASSINGNING RETURNS TIO DECLARED ARGS##############
   
   
   
   
   	for my $procedure (@proc_name3)
	{
		$MR->log_msg('shezanzarda33 '.$procedure);
		if ($#proc_name3 > -1)
		{
				
			
			$MR->log_msg("daiwyo $procedure $script");
			$script =~ s/(?<!def\s)$procedure\s*\((.*?)\)\s*\;/$1 = $pkg_name.$procedure($1);/gis;
			$script =~ s/(?<!def\s)$procedure\s*\;/$pkg_name.$procedure()/gis;
			$MR->log_msg("sheicvala $script");
			
		}
	}	
		
   
   
   ########################################################################################################

	$script =~ s/\s*CREATE\s+OR\s+REPLACE\s+PACKAGE\s+(\"*\w*\"*\.*\"*\w+\"*)\s*?(\bIS\b|\bAS\b)/class $pkg_name():\n\tpass\n#-- COMMAND ----------\n/gis;
	$script =~ s/CLASS\s+(\w+)\.(\w+)(\s*\(.*?\)\s*\:)(.*?)(\bpass\b)/class $1:\n\tclass $2$3$4\t$5/gis;

	$script =~ s/\s*(\w+)\s+\w+\s*\:\=(.*?)\;/\n$pkg_name.$1=$2\n#-- COMMAND ----------\n/gis;
	$script =~ s/\s*cursor\s+(\w+)\s*\(.*?\)\s*\bIS\b(.*?)\;/\n$pkg_name.$1="""$2"""#\n-- COMMAND ----------\n/gis;
	$script =~ s/\s*cursor\s+(\w+).*?\bIS\b(.*?)\b\;/\n$pkg_name.$1="""$2"""\n#-- COMMAND ----------\n/gis;
	$script =~ s/(def\s+\w+\s*\()/$1pkg,/gis;
	#$script =~ s/\%python//gis;
	if ($pkg_name =~/\w+\.\w+/gis){
		$pkg_name =~ s/\w+\.(\w+)/$1/gis;$MR->log_msg("package_name-----".$pkg_name);
	}
	
	$script =~ s/pkg\s*,\s*\)/pkg)/gis;
	$script =~ s/\h\h\h\h(\w+)/\t$1/gis;
	$script =~ s/END\s+$pkg_name\s*;\s*\///gis;
	$script =~ s/END\s*;\s*\///gis;
	return $script;
}
sub switch 
{
	my $ar = shift;
	my $script = join("\n", @$ar);
	$MR->log_msg("entering switch: $script");
	my $tab_tag = $CFG_POINTER->{tab_tag};
	$tab_tag =~ s/\%count\%/$PHYTON_SCOPE_LEVEL/gis;
	my $begin_tag = get_begin_tag();
	$script = $MR->trim($script);
	my ($switch) = $script =~ /switch\s\((.*?)\)/gis;
  	#switch\s*\(.*?\)\s*\{.*?\}
	$script =~ s/\}//gis;
	$script =~ s/\{\s*CASE(.*?)\:/if $switch == $1\{/gis;
	$script =~ s/CASE(.*?)\:/elsif $switch == $1\{/gis;
	$script =~ s/break\s*\;/\}/gis;
	$MR->log_msg("print_handler: script");
	
	return $script;
}

sub old_join
{
	my $ar = shift;
	my $script = join("\n", @$ar);

	my $tab_tag = $CFG_POINTER->{tab_tag};
	$tab_tag =~ s/\%count\%/$PHYTON_SCOPE_LEVEL/gis;
	my $begin_tag = get_begin_tag();
	$script = $MR->trim($script);
	$MR->log_msg("entering_old_join");
	if($script =~ /UNION\s+ALL/gis)
	{
		my @scripts = split /UNION\s+ALL/,$script; 
			my $jn_script = '';
			my $ln = scalar(@scripts);
			my $cnt =0;
			for my $scr (@scripts)
			{
				$cnt +=1; 
				if($cnt != $ln)
				{
					$scr = $scr.";";
				}
				
				my ($select) = $scr=~ /(.*?from\s+\w*\.*\w*\.*\w+\s*\w*\s*)\,/gis;
				#my ($body) = $script=~ /(from.*?where.*?\(\s*\+\s*\).*?\;)/gis;
				my ($tables) = $scr=~ /from(.*?)where/gis;
				my ($joins) = $scr =~ /where(.*?\;)/gis;
				my @tbls = split("\,",$tables);
				for my $jn(@tbls)
				{
					if( $jn =~ /(\w+)\s+(\w+)/gis)
					{
						
						my $tbl = $MR->trim($1);
						my $alias =$MR->trim($2);	
						$joins =~ s/(\w+\.\w+)\s*\=\s*(\Q$alias\E\.\w+)\s*\(\s*\+\s*\)/LEFT JOIN $tbl $alias on $2 = $1 /gis;
						$joins =~ s/(\w+\.\w+)\s*\>\s*(\Q$alias\E\.\w+)\s*\(\s*\+\s*\)/LEFT JOIN $tbl $alias on $2 > $1 /gis;
						$joins =~ s/(\w+\.\w+)\s*\<\s*(\Q$alias\E\.\w+)\s*\(\s*\+\s*\)/LEFT JOIN $tbl $alias on $2 < $1 /gis;
						$joins =~ s/(\w+\.\w+)\s*\>\=\s*(\Q$alias\E\.\w+)\s*\(\s*\+\s*\)/LEFT JOIN $tbl $alias on $2 >= $1 /gis;
						$joins =~ s/(\w+\.\w+)\s*\<\=\s*(\Q$alias\E\.\w+)\s*\(\s*\+\s*\)/LEFT JOIN $tbl $alias on $2 <= $1 /gis;
						
						$joins =~ s/(\w+\.\w+)\s*\(\s*\+\s*\)\s*\=\s*(\Q$alias\E\.\w+)\s*/RIGHT JOIN $tbl $alias on $2 = $1 /gis;
						$joins =~ s/(\w+\.\w+)\s*\(\s*\+\s*\)\s*\>\s*(\Q$alias\E\.\w+)\s*/RIGHT JOIN $tbl $alias on $2 > $1 /gis;
						$joins =~ s/(\w+\.\w+)\s*\(\s*\+\s*\)\s*\<\s*(\Q$alias\E\.\w+)\s*/RIGHT JOIN $tbl $alias on $2 < $1 /gis;
						$joins =~ s/(\w+\.\w+)\s*\(\s*\+\s*\)\s*\>=\s*(\Q$alias\E\.\w+)\s*/RIGHT JOIN $tbl $alias on $2 >= $1 /gis;
						$joins =~ s/(\w+\.\w+)\s*\(\s*\+\s*\)\s*\<=\s*(\Q$alias\E\.\w+)\s*/RIGHT JOIN $tbl $alias on $2 <= $1 /gis;
						$joins =~ s/AND\s+(\bLEFT\b|\bRIGHT\b)\s+JOIN/$1 JOIN/gis; 
						$joins =~ s/WHERE\s+(\bLEFT\b|\bRIGHT\b)/$1/gis;
					}
					elsif ($jn =~ /(\w+)/gis)
					{
						my $tbl = $MR->trim($1);
						my $alias =$MR->trim($1);	
						$joins =~ s/(\w+\.\w+)\s*\=\s*(\Q$alias\E\.\w+)\s*\(\s*\+\s*\)/LEFT JOIN $tbl $alias on $2 = $1 /gis;
						$joins =~ s/(\w+\.\w+)\s*\>\s*(\Q$alias\E\.\w+)\s*\(\s*\+\s*\)/LEFT JOIN $tbl $alias on $2 > $1 /gis;
						$joins =~ s/(\w+\.\w+)\s*\<\s*(\Q$alias\E\.\w+)\s*\(\s*\+\s*\)/LEFT JOIN $tbl $alias on $2 < $1 /gis;
						$joins =~ s/(\w+\.\w+)\s*\>\=\s*(\Q$alias\E\.\w+)\s*\(\s*\+\s*\)/LEFT JOIN $tbl $alias on $2 >= $1 /gis;
						$joins =~ s/(\w+\.\w+)\s*\<\=\s*(\Q$alias\E\.\w+)\s*\(\s*\+\s*\)/LEFT JOIN $tbl $alias on $2 <= $1 /gis;
						
						$joins =~ s/(\w+\.\w+)\s*\(\s*\+\s*\)\s*\=\s*(\Q$alias\E\.\w+)\s*/RIGHT JOIN $tbl $alias on $2 = $1 /gis;
						$joins =~ s/(\w+\.\w+)\s*\(\s*\+\s*\)\s*\>\s*(\Q$alias\E\.\w+)\s*/RIGHT JOIN $tbl $alias on $2 > $1 /gis;
						$joins =~ s/(\w+\.\w+)\s*\(\s*\+\s*\)\s*\<\s*(\Q$alias\E\.\w+)\s*/RIGHT JOIN $tbl $alias on $2 < $1 /gis;
						$joins =~ s/(\w+\.\w+)\s*\(\s*\+\s*\)\s*\>=\s*(\Q$alias\E\.\w+)\s*/RIGHT JOIN $tbl $alias on $2 >= $1 /gis;
						$joins =~ s/(\w+\.\w+)\s*\(\s*\+\s*\)\s*\<=\s*(\Q$alias\E\.\w+)\s*/RIGHT JOIN $tbl $alias on $2 <= $1 /gis;
						$joins =~ s/AND\s+(\bLEFT\b|\bRIGHT\b)\s+JOIN/$1 JOIN/gis; 
						$joins =~ s/WHERE\s+(\bLEFT\b|\bRIGHT\b)/$1/gis;
						
					}
				
				}	
			#$jn_script = $sql_parser->convert_sql_fragment($PREFIX_TAG.$tab_tag.$jn_script);	
			#$joins =~ s/\;//gis;
			if($cnt != $ln)
			{
				#$MR->log_msg("entered $scr");
				$joins =~ s/(.*)\;/$1/gis;
			}
			$jn_script = $jn_script.$select."\n".$joins."\n"."\nUNION ALL\n";
			$jn_script =~ s/\;\s+UNION\s+ALL/;/gis; 
			$MR->log_msg("entered $jn_script $cnt $ln");
			}
			
			
			$jn_script = $sql_parser->convert_sql_fragment($PREFIX_TAG.$tab_tag.$jn_script.";")  ;
			return $jn_script;
	}
	elsif($script =~ /\bUNION\b\s+SELECT/gis)
	{
		my @scripts = split /UNION/,$script; 
			my $jn_script = '';
			my $ln = scalar(@scripts);
			my $cnt =0;
			for my $scr (@scripts)
			{
				$cnt +=1; 
				if($cnt != $ln)
				{
					$scr = $scr.";";
				}
				
				my ($select) = $scr=~ /(.*?from\s+\w*\.*\w*\.*\w+\s*\w*\s*)\,/gis;
				#my ($body) = $script=~ /(from.*?where.*?\(\s*\+\s*\).*?\;)/gis;
				my ($tables) = $scr=~ /from(.*?)where/gis;
				my ($joins) = $scr =~ /where(.*?\;)/gis;
				my @tbls = split("\,",$tables);
				for my $jn(@tbls)
				{
					if( $jn =~ /(\w+)\s+(\w+)/gis)
					{
						
						my $tbl = $MR->trim($1);
						my $alias =$MR->trim($2);	
						$joins =~ s/(\w+\.\w+)\s*\=\s*(\Q$alias\E\.\w+)\s*\(\s*\+\s*\)/LEFT JOIN $tbl $alias on $2 = $1 /gis;
						$joins =~ s/(\w+\.\w+)\s*\>\s*(\Q$alias\E\.\w+)\s*\(\s*\+\s*\)/LEFT JOIN $tbl $alias on $2 > $1 /gis;
						$joins =~ s/(\w+\.\w+)\s*\<\s*(\Q$alias\E\.\w+)\s*\(\s*\+\s*\)/LEFT JOIN $tbl $alias on $2 < $1 /gis;
						$joins =~ s/(\w+\.\w+)\s*\>\=\s*(\Q$alias\E\.\w+)\s*\(\s*\+\s*\)/LEFT JOIN $tbl $alias on $2 >= $1 /gis;
						$joins =~ s/(\w+\.\w+)\s*\<\=\s*(\Q$alias\E\.\w+)\s*\(\s*\+\s*\)/LEFT JOIN $tbl $alias on $2 <= $1 /gis;
						
						$joins =~ s/(\w+\.\w+)\s*\(\s*\+\s*\)\s*\=\s*(\Q$alias\E\.\w+)\s*/RIGHT JOIN $tbl $alias on $2 = $1 /gis;
						$joins =~ s/(\w+\.\w+)\s*\(\s*\+\s*\)\s*\>\s*(\Q$alias\E\.\w+)\s*/RIGHT JOIN $tbl $alias on $2 > $1 /gis;
						$joins =~ s/(\w+\.\w+)\s*\(\s*\+\s*\)\s*\<\s*(\Q$alias\E\.\w+)\s*/RIGHT JOIN $tbl $alias on $2 < $1 /gis;
						$joins =~ s/(\w+\.\w+)\s*\(\s*\+\s*\)\s*\>=\s*(\Q$alias\E\.\w+)\s*/RIGHT JOIN $tbl $alias on $2 >= $1 /gis;
						$joins =~ s/(\w+\.\w+)\s*\(\s*\+\s*\)\s*\<=\s*(\Q$alias\E\.\w+)\s*/RIGHT JOIN $tbl $alias on $2 <= $1 /gis;
				
						$joins =~ s/AND\s+(\bLEFT\b|\bRIGHT\b)\s+JOIN/$1 JOIN/gis; 
						$joins =~ s/WHERE\s+(\bLEFT\b|\bRIGHT\b)/$1/gis;
					}
					elsif ($jn =~ /(\w+)/gis)
					{
						my $tbl = $MR->trim($1);
						my $alias =$MR->trim($1);	
						$joins =~ s/(\w+\.\w+)\s*\=\s*(\Q$alias\E\.\w+)\s*\(\s*\+\s*\)/LEFT JOIN $tbl $alias on $2 = $1 /gis;
						$joins =~ s/(\w+\.\w+)\s*\>\s*(\Q$alias\E\.\w+)\s*\(\s*\+\s*\)/LEFT JOIN $tbl $alias on $2 > $1 /gis;
						$joins =~ s/(\w+\.\w+)\s*\<\s*(\Q$alias\E\.\w+)\s*\(\s*\+\s*\)/LEFT JOIN $tbl $alias on $2 < $1 /gis;
						$joins =~ s/(\w+\.\w+)\s*\>\=\s*(\Q$alias\E\.\w+)\s*\(\s*\+\s*\)/LEFT JOIN $tbl $alias on $2 >= $1 /gis;
						$joins =~ s/(\w+\.\w+)\s*\<\=\s*(\Q$alias\E\.\w+)\s*\(\s*\+\s*\)/LEFT JOIN $tbl $alias on $2 <= $1 /gis;
						
						$joins =~ s/(\w+\.\w+)\s*\(\s*\+\s*\)\s*\=\s*(\Q$alias\E\.\w+)\s*/RIGHT JOIN $tbl $alias on $2 = $1 /gis;
						$joins =~ s/(\w+\.\w+)\s*\(\s*\+\s*\)\s*\>\s*(\Q$alias\E\.\w+)\s*/RIGHT JOIN $tbl $alias on $2 > $1 /gis;
						$joins =~ s/(\w+\.\w+)\s*\(\s*\+\s*\)\s*\<\s*(\Q$alias\E\.\w+)\s*/RIGHT JOIN $tbl $alias on $2 < $1 /gis;
						$joins =~ s/(\w+\.\w+)\s*\(\s*\+\s*\)\s*\>=\s*(\Q$alias\E\.\w+)\s*/RIGHT JOIN $tbl $alias on $2 >= $1 /gis;
						$joins =~ s/(\w+\.\w+)\s*\(\s*\+\s*\)\s*\<=\s*(\Q$alias\E\.\w+)\s*/RIGHT JOIN $tbl $alias on $2 <= $1 /gis;
						
					
						$joins =~ s/AND\s+(\bLEFT\b|\bRIGHT\b)\s+JOIN/$1 JOIN/gis; 
						$joins =~ s/WHERE\s+(\bLEFT\b|\bRIGHT\b)/$1/gis;
						
					}
				
				}
            if($cnt != $ln)
			{
				#$MR->log_msg("entered $scr");
				$joins =~ s/(.*)\;/$1/gis;
			}				
			#$jn_script = $sql_parser->convert_sql_fragment($PREFIX_TAG.$tab_tag.$jn_script);	
			$jn_script = $jn_script.$select."\n".$joins."\n"."\nUNION\n";
			$jn_script =~ s/\;\s+UNION\b/;/gis; 
			
			}
			$jn_script = $sql_parser->convert_sql_fragment($PREFIX_TAG.$tab_tag.$jn_script)  ;
			return $jn_script;
	}

	else
	{
	my ($select) = $script=~ /(.*?from\s+\w*\.*\w*\.*\w+\s*\w*\s*)\,/gis;
	
	#my ($body) = $script=~ /(from.*?where.*?\(\s*\+\s*\).*?\;)/gis;
	my ($tables) = $script=~ /from(.*?)where/gis;
	my ($joins) = $script=~ /where(.*?\;)/gis;
	my @tbls = split("\,",$tables);
	for my $jn(@tbls)
	{
		if( $jn =~ /(\w+)\s+(\w+)/gis)
		{
			
			my $tbl = $MR->trim($1);
			my $alias =$MR->trim($2);	
			$joins =~ s/(\w+\.\w+)\s*\=\s*(\Q$alias\E\.\w+)\s*\(\s*\+\s*\)/LEFT JOIN $tbl $alias on $2 = $1 /gis;
			$joins =~ s/(\w+\.\w+)\s*\>\s*(\Q$alias\E\.\w+)\s*\(\s*\+\s*\)/LEFT JOIN $tbl $alias on $2 > $1 /gis;
			$joins =~ s/(\w+\.\w+)\s*\<\s*(\Q$alias\E\.\w+)\s*\(\s*\+\s*\)/LEFT JOIN $tbl $alias on $2 < $1 /gis;
			$joins =~ s/(\w+\.\w+)\s*\>\=\s*(\Q$alias\E\.\w+)\s*\(\s*\+\s*\)/LEFT JOIN $tbl $alias on $2 >= $1 /gis;
			$joins =~ s/(\w+\.\w+)\s*\<\=\s*(\Q$alias\E\.\w+)\s*\(\s*\+\s*\)/LEFT JOIN $tbl $alias on $2 <= $1 /gis;
			
			$joins =~ s/(\w+\.\w+)\s*\(\s*\+\s*\)\s*\=\s*(\Q$alias\E\.\w+)\s*/RIGHT JOIN $tbl $alias on $2 = $1 /gis;
		    $joins =~ s/(\w+\.\w+)\s*\(\s*\+\s*\)\s*\>\s*(\Q$alias\E\.\w+)\s*/RIGHT JOIN $tbl $alias on $2 > $1 /gis;
			$joins =~ s/(\w+\.\w+)\s*\(\s*\+\s*\)\s*\<\s*(\Q$alias\E\.\w+)\s*/RIGHT JOIN $tbl $alias on $2 < $1 /gis;
			$joins =~ s/(\w+\.\w+)\s*\(\s*\+\s*\)\s*\>=\s*(\Q$alias\E\.\w+)\s*/RIGHT JOIN $tbl $alias on $2 >= $1 /gis;
			$joins =~ s/(\w+\.\w+)\s*\(\s*\+\s*\)\s*\<=\s*(\Q$alias\E\.\w+)\s*/RIGHT JOIN $tbl $alias on $2 <= $1 /gis;
			#$joins =~ s/\(\s*\+\s*\)//gis;
		    $joins =~ s/AND\s+(\bLEFT\b|\bRIGHT\b)\s+JOIN/$1 JOIN/gis; 
			$joins =~ s/WHERE\s+(\bLEFT\b|\bRIGHT\b)/$1/gis;
		}
		elsif ($jn =~ /(\w+)/gis){
			my $tbl = $MR->trim($1);
			my $alias =$MR->trim($1);	
			$joins =~ s/(\w+\.\w+)\s*\=\s*(\Q$alias\E\.\w+)\s*\(\s*\+\s*\)/LEFT JOIN $tbl $alias on $2 = $1 /gis;
			$joins =~ s/(\w+\.\w+)\s*\>\s*(\Q$alias\E\.\w+)\s*\(\s*\+\s*\)/LEFT JOIN $tbl $alias on $2 > $1 /gis;
			$joins =~ s/(\w+\.\w+)\s*\<\s*(\Q$alias\E\.\w+)\s*\(\s*\+\s*\)/LEFT JOIN $tbl $alias on $2 < $1 /gis;
			$joins =~ s/(\w+\.\w+)\s*\>\=\s*(\Q$alias\E\.\w+)\s*\(\s*\+\s*\)/LEFT JOIN $tbl $alias on $2 >= $1 /gis;
			$joins =~ s/(\w+\.\w+)\s*\<\=\s*(\Q$alias\E\.\w+)\s*\(\s*\+\s*\)/LEFT JOIN $tbl $alias on $2 <= $1 /gis;
			
			$joins =~ s/(\w+\.\w+)\s*\(\s*\+\s*\)\s*\=\s*(\Q$alias\E\.\w+)\s*/RIGHT JOIN $tbl $alias on $2 = $1 /gis;
		    $joins =~ s/(\w+\.\w+)\s*\(\s*\+\s*\)\s*\>\s*(\Q$alias\E\.\w+)\s*/RIGHT JOIN $tbl $alias on $2 > $1 /gis;
			$joins =~ s/(\w+\.\w+)\s*\(\s*\+\s*\)\s*\<\s*(\Q$alias\E\.\w+)\s*/RIGHT JOIN $tbl $alias on $2 < $1 /gis;
			$joins =~ s/(\w+\.\w+)\s*\(\s*\+\s*\)\s*\>=\s*(\Q$alias\E\.\w+)\s*/RIGHT JOIN $tbl $alias on $2 >= $1 /gis;
			$joins =~ s/(\w+\.\w+)\s*\(\s*\+\s*\)\s*\<=\s*(\Q$alias\E\.\w+)\s*/RIGHT JOIN $tbl $alias on $2 <= $1 /gis;
			$MR->log_msg("enteredold_join1 $joins");
			
			
		    $joins =~ s/AND\s+(\bLEFT\b|\bRIGHT\b)\s+JOIN/$1 JOIN/gis; 
			$joins =~ s/WHERE\s+(\bLEFT\b|\bRIGHT\b)/$1/gis;
			
			$MR->log_msg("enteredold_join $joins");
		}
	
	}
	$script = $select."\n".$joins."\n";	
	$script = $sql_parser->convert_sql_fragment($PREFIX_TAG.$tab_tag.$script);
	$script =~ s/\(\s*\+\s*\)//gis;
	}
	return $script;
}

sub print_handler
{
	my $ar = shift;
	my $script = join("\n", @$ar);
	$MR->log_msg("print_handler: $script");
	my $tab_tag = $CFG_POINTER->{tab_tag};
	$tab_tag =~ s/\%count\%/$PHYTON_SCOPE_LEVEL/gis;
	my $begin_tag = get_begin_tag();
	$script = $MR->trim($script);
	$script =~ s/dbms_output\.put_line/print/gis; 
	$MR->log_msg("print_handler: script");
	
	return $script;
}

sub copy_into_files
{
	my $ar = shift;
	my $script = join("\n", @$ar);
	my ($table) = $script =~/copy\s+into\s+(\w+\b)/gis;
	my $path ='';
	($path) = $script =~/from\s+(.*?)\s+credentials/gis;
	if($path eq ''){
		($path) = $script =~/from\s+\'(.*?)\'/gis;	
	}
	$MR->log_msg("copy_into_files: $path");
	if($path !~ /\'/gis)
	{
	$path = "'".$path."'";
	}
	my($format)=$script =~/format_name\s*\=(.*?)\)/gis;
	my ($secret_key) = $script =~/aws_secret_key\s*\=\s*(\'.*?\')/gis;
	my ($aws_key_id) = $script =~/aws_key_id\s*\=\s*(\'.*?\')/gis;
	
	$secret_key =~ s/\$(\b\w+\b)/\${$1}/gis;
	$aws_key_id =~ s/\$(\b\w+\b)/\${$1}/gis;
	if ("$script" =~/(AZURE_SAS_TOKEN\s*\=\s*\'.*?\')/gis)
	{
		$script = "COPY INTO ".$table."\nFROM ".$path."\nWITH (\nCREDENTIAL (".$1.")\n"
		."ENCRYPTION (TYPE='AZURE_CSE', MASTER_KEY=''kPx...'')\n)\nFILEFORMAT = ".$format.";";
	}
	elsif ($script =~/type\s*\=\s*\'AZURE_CSE\'/gis)
	{
		$script = "COPY INTO ".$table."\nFROM "."$path"."\nWITH (\nENCRYPTION (TYPE='AZURE_CSE', MASTER_KEY=''kPx...'')\n)"
        ."FILEFORMAT = ".$format.";";		     	
	}
	
	else 
	{
		$script = "COPY INTO ".$table."\nFROM ".$path."\nWITH (\nCREDENTIAL (AWS_ACCESS_KEY=".$aws_key_id." , AWS_SECRET_KEY=".$secret_key.")\n"
		."ENCRYPTION (MASTER_KEY=''kPx...'')\n)\nFILEFORMAT = ".$format.";";
    }
	$script ="-- FIXME databricks.migration.task Update 'File/Folder Location' for Datbricks workspace.\n".
	"-- FIXME databricks.migration.task Review/Update 'File Format/Options' for Datbricks.\n".
	"-- REF https://docs.databricks.com/sql/language-manual/delta-copy-into.html\n".$script; 
	
	return $script;
}






sub load_data
{
	my $ar = shift;
	my $script = join("\n", @$ar);
	#$MR->log_msg("load_data_handler: $script");
	my $src='';
	my $badfile ='';
	my $delimiter='';
	my $enclosed ='';
	if($script !~ /INFILE\s+(\'.*?\')/gis)
	{
		($src) = "$script" =~ /INFILE\s+(\".*?\")/gis;	
	}
	else
	{
		($src) = "$script" =~ /INFILE\s+(\'.*?\')/gis;
	}
	
	if($script !~ /BADFILE\s+(\'.*?\')/gis)
	{		
		($badfile) = "$script" =~ /BADFILE\s+(\".*?\")/gis;
	}
	else
	{
		($badfile) = "$script" =~ /BADFILE\s+(\'.*?\')/gis;
	}
	
	if($script !~ /FIELDS\s+TERMINATED\s+BY\s+\"(.*?)\"/gis)
	{		
		($delimiter) = "$script" =~ /FIELDS\s+TERMINATED\s+BY\s+\'(.*?)\'/gis;
	}
	else
	{
		($delimiter) = "$script" =~ /FIELDS\s+TERMINATED\s+BY\s+\"(.*?)\"/gis;
		
	}
	
	if($script !~ /OPTIONALLY\s+ENCLOSED\s+BY\s+\'(.*?)\'/gis)
	{		
		($enclosed) = "$script" =~ /OPTIONALLY\s+ENCLOSED\s+BY\s+\"(.*?)\"/gis;
	}
	else
	{
		($enclosed) = "$script" =~ /OPTIONALLY\s+ENCLOSED\s+BY\s+\'(.*?)\'/gis;
		
	}
	
	
	
	
	$MR->log_msg("load_data_handlerzzz: $delimiter");
	
	my ($dateformat) = $script =~ /date\s+(\'.*?\')/gis;
	#my ($enclosed) = $script =~ /OPTIONALLY\s+ENCLOSED\s+BY\s+\'(.*?)\'/gis;
	my ($columns) =  $script =~ /\((.*?)\)\s*\;/gis;
	my ($table) = $script =~ /INSERT\s+\INTO\s+\TABLE\s+(\w+)/gis;

    my @clns =  split("\,", $columns);
	my $select = "SELECT \n";
	foreach my $cl (@clns)
	{
		if($cl=~/(\w+)\s+(\w+)/gis)
		{
			$select = $select."\t".$MR->trim($1).'::'.$MR->trim($2).",\n";	
		}
		else
		{
			$select = $select.$cl.",\n";	
		}		
	
	
	}
	my $final_script = $script;
	if ($enclosed =~ "'")
	{
	
	$final_script = "COPY INTO ".$table."\nFROM(\n"
					.$select."\nFROM ".$src."\n)FILE FORMAT = CSV\nFORMAT_OPTIONS (\n\t"
					."'badRecordsPath' = ".$badfile."\n\t,"
					."'delimiter' = "."'"."$delimiter"."'"."\n\t,"
					."'quote' = ".'"'."$enclosed".'"'."\n\t,"
					."'dateFormat' =".$dateformat."\n);" ;
		
	}
	else 
	{
	$final_script = "COPY INTO ".$table."\nFROM(\n"
					.$select."\nFROM ".$src."\n)\nFILE FORMAT = CSV\nFORMAT_OPTIONS (\n\t"
					."'badRecordsPath' = ".$badfile."\n\t,"
					."'delimiter' = "."'"."$delimiter"."'"."\n\t,"
					."'quote' = "."'"."$enclosed"."'"."\n\t,"
					."'dateFormat' =".$dateformat."\n);" ;
	}
	$final_script =~ s/\,\s*FROM\b/\nFROM/gis;
	
	if("$script" !~ /APPEND/gis)
	{
	$final_script = 
	"-- Mapped Databricks output\n"
	."-- FIXME databricks.migration.task Update 'File/Folder Location' for Datbricks workspace.\n"
	."-- FIXME databricks.migration.task Review/Update 'File Format/Options' for Datbricks."
	."-- REF https://docs.databricks.com/sql/language-manual/delta-copy-into.html\n"
	."-- FIXME databricks.migration.unsupported (source:SQL*Loader) no empty table checks before insert without APPEND\n"
	.$final_script;	
	}
	else 
	{
	$final_script =
	"-- Mapped Databricks output\n"
	."-- FIXME databricks.migration.task Update 'File/Folder Location' for Datbricks workspace.\n"
	."-- FIXME databricks.migration.task Review/Update 'File Format/Options' for Datbricks."
	."-- REF https://docs.databricks.com/sql/language-manual/delta-copy-into.html\n"
	.$final_script;
	
	}
	
	#$MR->log_msg("print_handler: script");
	
	return $final_script."\n-- COMMAND ----------\n";
}




sub bind_var
{
	my $ar = shift;
	my $script = join("\n", @$ar);
	$MR->log_msg("binder_var: $script");
	
	my $tab_tag = $CFG_POINTER->{tab_tag};
	$tab_tag =~ s/\%count\%/$PHYTON_SCOPE_LEVEL/gis;
	my $begin_tag = get_begin_tag();
	$script = $MR->trim($script);
	my ($bnds) = $script =~ /sqlText\:.*?\,\s*BINDS\:\s*\[(.*?)\]/gis;
	my ($body) = $script =~ /sqlText\:(.*?)\,\s*BINDS\:\s*\[.*?\]/gis;
	
	
	my @bnd_vars =  split("\,", $bnds);
	for my $bnd(@bnd_vars)
	{
		if($body !~ /\bcall\b/gis){
			$bnd=~s/(\w*\.*\w+)/{$1}/gis;
			$bnd=~s/\{(\d+)\}/$1/gis;
		}
		$body =~ s/\?/$bnd/is; 	
	}
	
	
	$script =~ s/sqlText\:(.*?)BINDS\:\s*(\[.*?\])/sqlText\:$body/gis; 
	
		
	
	$script = $sql_parser->convert_sql_fragment($PREFIX_TAG.$tab_tag.$script);

	
	return $script;
}

sub fetch_into
{
	my $ar = shift;
	my $script = join("\n", @$ar);
	$MR->log_msg("FETCH_INTO_HANDLER: $script");
	my $tab_tag = $CFG_POINTER->{tab_tag};
	$tab_tag =~ s/\%count\%/$PHYTON_SCOPE_LEVEL/gis;
	my $begin_tag = get_begin_tag();
	$script = $MR->trim($script);
	
	if($script =~ /LOOP\s+FETCH\s+(\w+)\s+into\s+(\w+)\s+(.*)\;/gis){
		my $column_list = $3;
		$MR->log_msg("print_handler: $column_list");
		my $row_nm = $1;
		my $crs_nm = $2;
		$column_list =~ s/\s*(\w+)\s*\,*\s*/\t$1 =  $row_nm ["_COLUMN_NAME_FROM_SELECT_"];# FIX ME please plug in column name from cursor declaration\n/gis;
		
		$script = $PREFIX_TAG.$tab_tag."for ".$row_nm." in ".$crs_nm."\n".$column_list;
		
	}
	
	elsif($script =~/LOOP\s+FETCH\s+(\w+)\s+into\s+(\w+\s*\,.*?)\;/gis)
	{
		my $column_list = $2;
		$MR->log_msg("print_handler: $column_list");
		my $row_nm = $1."_rec";
		my $crs_nm = $1;
		$column_list =~ s/\s*(\w+)\s*\,*\s*/\t$1 =  $row_nm ["_COLUMN_NAME_FROM_SELECT_"];# FIX ME please plug in column name from cursor declaration\n/gis;
		
		$script = $PREFIX_TAG.$tab_tag."for ".$row_nm." in ".$crs_nm."\n".$column_list;
		
	}
	
	$script = $sql_parser->convert_sql_fragment($script);

	return $script;
}

sub wrap_args
{
	my $script = shift;
	
    foreach my $arg_def (@{ $Globals::ENV{PRESCAN}->{PROC_ARGS} })
	{
		my $nrg = $arg_def->{NAME};
		my $tp = $arg_def->{ARG_TYPE};
		$MR->log_msg("entering wrap_args: ".$tp);
		if($nrg !~/cursor/is and "$script" =~ /(insert|delete|update|merge|select|alter)/gis and $MR->trim($tp) !~ /INOUT/gis)
		{
			$script =~s/(?<!\{)(\b$nrg\b)/{$1}/gis;
		}
	}
	foreach my $var_def (@{ $Globals::ENV{PRESCAN}->{PROC_VARS} })
	{
		my $nrg =$var_def->{NAME};
	
		if($nrg !~/cursor/is and "$script" =~ /(insert|delete|update|merge|select|alter)/gis )
		{
			$script =~s/(?<!\{)(\b$nrg\b)/{$1}/gis;
		}
	}
	foreach my $arg_def (@{ $Globals::ENV{PRESCAN}->{FUNCTION_ARGS} })
	{
		my $nrg =$arg_def->{NAME};
		my $tp= $arg_def->{ARG_TYPE};
		$MR->log_msg("entering wrap_args: ".$tp);
		$MR->log_msg("wrap_args_cur_outer: ".$nrg."____".$script);
		if($nrg !~/cursor/is and "$script" =~ /(insert|delete|update|merge|select|alter)/gis and $MR->trim($tp) !~/INOUT/gis)
		{
			$MR->log_msg("wrap_args_cur_inner: ".$nrg."____".$script);
			$script =~s/(?<!\{)(\b$nrg\b)/{$1}/gis;
		}
	}
	foreach my $var_def (@{ $Globals::ENV{PRESCAN}->{FUNCTION_VARS} })
	{
		my $nrg =$var_def->{NAME};
	
		if($nrg !~/cursor/is and "$script" =~ /(insert|delete|update|merge|select|alter)/gis )
		{
			$script =~s/(?<!\{)(\b$nrg\b)/{$1}/gis;
		}
	}
	#$script = $sql_parser->convert_sql_fragment($PREFIX_TAG.$tab_tag.$script);
	return $script;
}


sub cte
{
	my $ar = shift;
	my $tab_count = 0;
	
	my $cont_string = join("\n", @$ar);
	my ($main_view) = $cont_string =~ /(CREATE.*?\bVIEW\b.*?\bAS\b)\s+WITH\s+/is;
	$cont_string =~ s/CREATE.*?\bVIEW\b.*?\bAS\b\s+WITH\s+//is;
	my @cte_ar = split //, $cont_string;
	
	$MR->log_msg("CTE_ARRAY_CONT_".Dumper(@cte_ar)."CONT_CTE_ARRAY");
	my @cte_array = ();
	my @remainder = ();
	my $prn =0;
	my $quote=0;
	my $cte ='';
	my $ln = scalar(@cte_ar);
	my $cnt=0;
	foreach my $char (@cte_ar)
	{
		
		$cnt += 1;
		$cte=$cte.$char;
		if($char eq '(')
		{
			
			$prn += 1;
			#$MR->log_msg("CTE_ARRAY_SPLIT"."$char".$prn);
		}
		elsif($char eq "'"){
			if($quote>0){
				$quote -=1;
			}
			else{
				$quote +=1;
			}
		}
		elsif($char eq ')' and $quote == 0)
		{
			if ($prn>0)
			{
				$prn-=1;
			}
			if($prn==0)
			{
				
				if($cte =~ /(\w+)\s+\bAS\b\s+(\(.*)/gis)
				
				{			
					my $t_name=$1;
					my $bdy =$2;
					my $final = $TEMP_VIEW_CREATION_STATEMENT;
					$final =~ s/\%TABLE_NAME\%/$t_name/gis;
					$final =~ s/\%INNER_SQL\%/$bdy/gis;
					#$cte = "CREATE TEMP VIEW ".$cte.";";
					$final =~ s/VIEW\s+\,/CREATE TEMP VIEW /is;
					push(@cte_array,$final);
					$cte='';
					$prn =0;
					$quote=0;
				}
				
				else
				{
					push(@remainder,$cte);	
					$cte='';
					$prn =0;
					$quote=0;
				}
			}
			
		}
		elsif($cnt==$ln){
			
		push(@remainder,$cte);	
					$cte='';
					$prn =0;
					$quote=0;
		}
}
my $replaced  = join("\n", @cte_array);
my $remainder = join("\n", @remainder);
my $content = $replaced."\n".$main_view."\n".$remainder;
#my @rt = split(/\n/,$content);
$MR->log_msg("MAIN_VIEW".$content);
$MR->log_msg("reached_the_end $remainder");
$MR->log_msg("CTE_ARRAY_START".Dumper(@cte_array)."CTE_ARRAY_END");
$content = $sql_parser->convert_sql_fragment($content);
return $content ;

}


sub table_keyword_removal
{
	my $ar = shift;
	my $tab_count = 0;
	
	my $cont_string = join("\n", @$ar);
	
	my @char_ar = split //, $cont_string;
	
	#$MR->log_msg("CTE_ARRAY_CONT_".Dumper(@cte_ar)."CONT_CTE_ARRAY");

    my $prn =0;
	my $str ='';
	my $quote =0;
	foreach my $char (@char_ar)
	{
		
		
		$str=$str.$char;
		if($char eq '(')
		{
			
			$prn += 1;
			#$MR->log_msg("CTE_ARRAY_SPLIT"."$char".$prn);
		}
		elsif($char eq "'"){
			if($quote>0)
			{
				$quote -=1;
			}
			else
			{
				$quote +=1;
			}
		}
		elsif($char eq ')' and $quote == 0)
		{
			if ($prn>0)
			{
				$prn-=1;
			}
			if($prn==0)
			{
				
				return $sql_parser->convert_sql_fragment($str.";");
				
			}
			
		}


	}

}

sub tab_counter_for_js
{
	my $ar = shift;
	my $tab_count = 0;
	
	my $cont_string = join("\n", @$ar);

	$cont_string =~ s/(\bsnowflake\.execute\b\s*\(\s*)\{(.*?)\}/$1_BEGIN_STMT_$2_END_STMT_/gis;
	$cont_string =~ s/(\bsnowflake\.createStatement\b\s*\(\s*)\{(.*?)\}/$1_BEGIN_STMT_$2_END_STMT_/gis;
	@$ar = split("\;", $cont_string);
	my @output_array = ();
	foreach my $l (@$ar)
	{
		my $tab_tag = $CFG_POINTER->{tab_tag};
		$tab_tag =~ s/\%count\%/$tab_count/gis;
		foreach my $char (split('', $l))
		{
			if($char eq '{')
			{
				$tab_count += 1;
			}
			elsif($char eq '}')
			{
				$tab_count -= 1;
			}
		}
		$l =~ s/_BEGIN_STMT_/{/gis;
		$l =~ s/_END_STMT_/}/gis;
		$l = $tab_tag.$l.";";
		push(@output_array,$l);
	}
	return \@output_array;
}

sub unpivot_to_stack
{
	my $cont = shift;

	if ($cont =~ /\bFROM\s+(\w+)\s+UNPIVOT\b(.*?)\(\s*(\w+)\s+\bFOR\s+(\w+)\s+.*?\((.*?)\)/gis)
	{
		my $table_name = $1;
		my $include_exclude_nulls = $MR->trim($2);
		my $unpivot_clause = $3;
		my $unpivot_for_clause = $4;
		my $unpivot_in_clause = $MR->trim($5);
		
		my @pivot_columns = split(/\,/,$unpivot_in_clause);
		my $column_count = scalar(@pivot_columns);
		
		my $converted_unpivot_in_clause;
		foreach my $pivot_column (@pivot_columns)
		{
			if ($converted_unpivot_in_clause)
			{
				$converted_unpivot_in_clause .= ",\n";
			}
			
			my @expression = split(/\bAS\b/i,$pivot_column);
			$expression[0] = $MR->trim($expression[0]);
			$expression[1] = $MR->trim($expression[1]);
			$converted_unpivot_in_clause .= "$expression[1], $expression[0]";
		}
		
		my $final_expression = $CFG_POINTER->{commands}->{UNPIVOT_TO_STACK};
		if ($include_exclude_nulls ne 'INCLUDE NULLS')
		{
			$final_expression = $CFG_POINTER->{commands}->{UNPIVOT_TO_STACK_INCLUDE_NULLS_WHERE};
		}
		
		$final_expression =~ s/\%COLUMN_COUNT\%/$column_count/gis;
		$final_expression =~ s/\%CONVERTED_UNPIVOT_IN_CLAUSE\%/$converted_unpivot_in_clause/gis;
		$final_expression =~ s/\%UNPIVOT_FOR_CLAUSE\%/$unpivot_for_clause/gis;
		$final_expression =~ s/\%UNPIVOT_CLAUSE\%/$unpivot_clause/gis;
		$final_expression =~ s/\%TABLE_NAME\%/$table_name/gis;

		return $final_expression;
	}
	return $cont;
}
sub convert_function
{   
	my $content = shift;
	my $cont = join("\n", @$content);
    $cont =~ s/\$\$//gis;
    
    $cont =~ s/(.*?)select/$1RETURN_FUNCTION select /im;
    if($cont!~/select/gis){
		$cont =~ s/(returns\s+.*?)\bAS\b/$1RETURN_FUNCTION/gis;
	}
	else
	{
	$cont =~ s/(returns\s+.*?)\bAS\b/$1/gis;
	}
    if($cont!~/\;/gis)
	{
	   $cont =$cont.";";
	}
   	$cont =~ s/CREATE\s+FUNCTION/CREATE OR REPLACE FUNCTION/gis;
	$cont =~ s/\s+RETURN_FUNCTION/\nRETURN_FUNCTION/gis;   
    return $cont;
}	

sub finalize_content
{
	my $ar = shift;
	my @ar2 ={};
	my $i = 0;
	
	for my $a (@$ar)
	{
		
		
		if ($IS_PYTHON_SCRIPT or  $IS_SCRIPT)
		{
			
			
			if($a =~ /(^\s*)\-\-/gis)
			{
				$a =~ s/(^\s*)\-\-/$1#/gis;
			}
			if($a =~/\/\*.*?\*\s*\//gis)
			{	
				
				my $comment1 = $a =~/\/\*.*?\*\s*\//gis;
				my @comment = "$a" =~/\/\*.*?\*\s*\//gims;
				$MR->log_msg("final_script_start".Dumper($a)."final_script_END");
				for my $cm (@comment){
				my $cm1 = $cm;
				$cm =~ s/(^\s*)/$1\#/gim;
				$cm =~ s/(\/\*)/\#$1/gis;
				$a =~ s/\Q$cm1\E/$cm/gis;
				}
			}
			
			
			@$ar[$i]= $a;
	
			$i=$i+1;
		 }
        		
		#push(@ar2, $a);	
		
	}


	
	if ($#FINAL_SCRIPT > 0){
	
		my $content = join("\n", @FINAL_SCRIPT);
		$content =~ s/(\d+)\_SUB\_ONE/$1-1/ge;
		$content = $USE_PREFIX.$content;
		@$ar = split(/\n/,$content);
		return $ar;
	}
	my $content = join("\n", @$ar);
	#$MR->log_error($content);
	$content =~ s/\_COMMENT\_/--/gis;

	if($is_exception or $IS_SCRIPT)
	{
		$content =~ s/\-+\s*COMMAND\s*\-+//gis;
		#$content =~ s/\%python//gis;
		$content =~ s/\n\s+\_\_REMOVE\_\_/\n/gis;
		#$content = "%python\n".$content;
		
		
		#$content =~ s/\/\*(.*?)\*\//"""$1"""/gis;
		$content =~ s/\<tab_count\:1\>/\t/gis;
    }

	
	$content =~ s/\_\_CURSOR\_SUFIX\_\_/$CURSOR_SUFIX/gis;
	$content =~ s/CURSOR\s*\=\s*\"\"//gis;
	$content =~ s/spark\.conf\.set\(\'var\.CURSOR\'\,\s*CURSOR\)//gis;
	$content =~ s/(\%python.*?)SET\s+var/$1\n-- COMMAND ----------\nSET var/gis;
	$content =~ s/(\-\- COMMAND \-\-\-\-\-\-\-\-\-\-)\s+(IF|WHILE|FOR|SPARK|\()/$1\n%python\n$2/gis;
	$content =~ s/([^\-\s])(\s+\%sql)/$1\n-- COMMAND ----------\n$2/gis;
	$content =~ s/-- COMMAND ----------\n+-- COMMAND ----------/-- COMMAND ----------\n/gis;
	$content =~ s/(before\.count\(\)\s+)(\w+)/$1\t$2/gis;
	$content =~ s/PYTHON\_COMMAND/COMMAND/gis;
	
    if($SRC_TYPE eq 'SNOWFLAKE')
	{
		$content =~ s/\:\s*\;/:/gis;
		$content =~ s/\;\s*\;//gis;
		$content =~ s/\s*\;/;/gis;
		$content =~ s/\:\s*\;/:/gis;
		$content =~ s/\s+\}//gis;
		$content =~ s/\;\s+\'/;'/gis;
#		$content =~ s/(\<tab_count:\d+\>)\s*\<tab_count:\d+\>/$1/gis;
#		$content =~ s/\<tab_count\:0\>(\n*)\t*\s*/$1/gis;
#		$content =~ s/\<tab_count\:1\>(\n*)\t*\s*/$1\t/gis;
#		$content =~ s/\<tab_count\:2\>(\n*)\t*\s*/$1\t\t/gis;
#		$content =~ s/\<tab_count\:3\>(\n*)\t*\s*/$1\t\t\t/gis;
#		$content =~ s/\<tab_count\:4\>(\n*)\t*\s*/$1\t\t\t\t/gis;
#		$content =~ s/\<tab_count\:5\>(\n*)\t*\s*/$1\t\t\t\t\t/gis;
	}	
	if ($CFG_POINTER->{change_procedure_to_function})
	{
		
		$content =~ s/dbutils\.notebook\.exit/return/gis;
	}
	else
	{
		

		if ($content =~ /\breturn\b\s*(\(.*?\))/gis)
		{
			my @rts ="$content"=~ /\breturn\b\s*\((.*?)\)/gis;
			$MR->log_error(Dumper(@rts));
			for my $rtrns(@rts)
			{
				my @args = split(/\,/,$rtrns);
				my $js = '{';
				for my $arg (@args)
				{
				$js = $js.'"'.$arg.'":'.$arg.",";
					
				}
				$js=$js.'}';
				$js =~ s/\,\s*\}/}/gis;
				$content =~ s/\breturn\b\s*(\(.*?\))/dbutils.notebook.exit($js)/gis;
				
			}

		}
		

	    $content =~ s/\breturn\b/dbutils.notebook.exit/gis;
	}
	
	$content =~ s/                        (\w+)/\t\t\t\t\t\t$1/gis;
	$content =~ s/                    (\w+)/\t\t\t\t\t$1/gis;
	$content =~ s/                (\w+)/\t\t\t\t$1/gis;
    $content =~ s/            (\w+)/\t\t\t$1/gis;
	$content =~ s/        (\w+)/\t\t$1/gis;
	$content =~ s/    (\w+)/\t$1/gis;
	$content =~ s/(\d+)\_SUB\_ONE/$1-1/ge;
	$content =~ s/\w+\s*\=\s*f\"\s*call\s+(\w*\.*\w+.*?)\"\s*\;\s+\w+\s*\=\s*spark\.sql\s*\(\s*stmt\s*\)\;*\s+(\w+)\s*\=\s*\w+\.head\(\)\[0\]\;/$2 = $1/gis;
	$content =~ s/spark\.sql\(\"\"\"\s*call\s+(.*?)\)\s*\"\"\"/$1/gis;
	$content =~ s/Exception\(\{(\w+)\}\)/Exception($1)/gis;

	#my @calls = $content =~/\w+\s*\=\s*f\"\s*call\s+\w*\.*\w+.*?\"\s*\;\w+\s*=\s*spark\.sql\(\w+)\s*\;\s+\w+\s*\=\s+\w+\.head\(\)\[0\]\;/gis;
	#	for my $cl (@calls){
	#		if($cl =~/(\w+)\s*\=\s*f\"\s*call\s+(\w*\.*\w+)(.*?\")\s*\;/gis){
	#		 my $main_var =$1;
	#		 my $pr_nm = $2;
    #         my $pr_body =$3;
	#		 my $int_var = $content =~ /\w+\s*=\s*spark\.sql\(\Q$main_var\E\)\s*\;/i;
	#		 
	#		 $MR->log_msg("calls_found $main_var --$pr_nm ---$pr_body--$content");
	#		 
	#		 $content =~ s/\w+\s*=\s*spark\.sql\(\Q$main_var\E\)\s*\;\s+\w+\s*\=\s+res\.head\(\)\[0\]\;//i; 
	#		 
	#		}
	#	}
		
	#adding use catalog at the top the files
	$content = $USE_PREFIX.$content;
	#adding target catalogs to create view and their usage very project specific.
	if(@CATALOGS)
	{
		foreach my $ctlg (@{ $CFG{catalogs} })
		{
		#$MR->log_msg("printing_catalogs ".Dumper($ctlg)."--->");
			foreach my $key(keys %$ctlg)
			{
			
				my $value =$ctlg->{$key};
				my $CATALOG=$key;
			    foreach my $schm($value)
				{
					#$MR->log_msg("printing_catalogs ".$key."--->".Dumper($value));	
					foreach my $vl(@$value)
					{
					
					
					
					
						my @view_list = $content =~/REPLACE\s+VIEW\s+(\Q$vl\E\.*\w+\b(?!\.))/gis;
						for my $vs (@view_list)
						{
							$MR->log_msg("printing_catalogs ".$vs);	
							$content =~ s/REPLACE\s+VIEW\s+\Q$vs\E/REPLACE VIEW $CATALOG.$vs/gis;
							$content =~ s/\bEXISTS\s+\Q$vs\E/EXISTS $CATALOG.$vs/gis;
							$content =~ s/\bON\s+\Q$vs\E/ON $CATALOG.$vs/gis;
				
							$content =~ s/(from|join)\s+\Q$vs\E/$1 $CATALOG.$vs/gis;
							$MR->log_msg('views_list '.$vs); 
						}
					
					}
				}
			}
		}
	}
	
	#changing  concat and is null to ''
	$content =~ s/CONV\_START\_(.*?)\_CONV_END\s+IS\sNULL/$1 = ''/gim;
	$content =~ s/CONV\_START\_(.*?)\_CONV_END(\s*\|\|)/NVL ($1,'')$2/gis;
	$content =~ s/(\|\|\s*)CONV\_START\_(.*?)\_CONV_END/$1 NVL($2,'')/gis;
	$content =~ s/CONV\_START\_(.*?)\_CONV_END/NVL($1,'')/gis;
	$content =~ s/(\|\|\s*)(\w+\.\w+)\s*\)/$1 NVL($2,'') )/gis;
	$content =~ s/\(\s*(\w+\.\w+)(\s*\|\|)/( NVL($1,'') $2/gis;
	$content =~ s/\_done//gis;
	$content =~ s/(\w+)\s*\=\s*\"\"\s*cursor/$1 cursor/gis;
	$content =~ s/(\w+)\s*\=\s*\"\"\s+spark\.conf\.set\(\'var\.\w+\b\'\,\s+\w+\b\s*\)\s*cursor/$1 cursor/gis;
	$content =~ s/(\w+)\s+CURSOR\s+for(.*?)\;/$1 = spark.sql(f\"\"\"$2\"\"\")/gis;
	$content =~ s/\$\$\s*\;/;/gis;
	$content =~ s/\;\;//gis;
	$content =~ s/RETURN_FUNCTION/RETURN/gis;
	$content =~ s/\{sql\}/sql/gis;
	#$MR->log_msg("exiring_function_proc_args $nb_main");
    
	if ($TRANSACTION_CONTROL)
	{
		$content =~ s/BEGIN\s+TRANSACTION/$INCREMENTAL_WORKLOAD_HEADER/gim;
		$content =~ s/\;\s+COMMIT\s*\;/$INCREMENTAL_WORKLOAD_FOOTER/gim;
	}
	if($REMOVE_COMMIT_AND_ROLLBACK)
	{
		$content =~ s/\bCOMMIT\b/#COMMIT/gim;
		$content =~ s/\bROLLBACK\b/#COMMIT/gim;
	}
	if ($CFG_POINTER->{change_procedure_to_function})
	{
		my $function_name = $Globals::ENV{PRESCAN}->{FUNCTION_NAME};
		
		my $return_type = $Globals::ENV{PRESCAN}->{FUNCTION_RETURN_TYPE};
		my $spark_type = "StringType()";
		if ($return_type =~/(\bDATE\b|\bTIMESTAMP)\b/gis)
		{
				$spark_type = "DateType()";

		}

		elsif ($return_type =~/\bfloat\b/gis)
		{
				$spark_type = "FloatType()";

		}

		elsif ($return_type =~/(\dec\b|number\s*\()/gis)
		{
				$spark_type = "DecimalType()";

		}

		elsif ($return_type =~/int/gis)
		{
				$spark_type = "IntegerType()";

		}


		$content=$content."\n"."spark.udf.register(\"$function_name\", $function_name, $spark_type)";
		
		#$MR->log_error(Dumper($Globals::ENV{PRESCAN}));


	}
	
	#$content =~ s/\_CONV_END//gis;
	@$ar = split(/\n/,$content);
	$PHYTON_SCOPE_LEVEL = 0;
	$BEGIN_LEVEL = 0;
	delete $Globals::ENV{PRESCAN};
	delete $Globals::ENV{CONFIG};
	return $ar;	
}



sub cursor_with_param
{
	my $cont = shift;
	my $cont = join("\n", @$cont);
	
	my ($cur,$params) =$cont=~ /(\b\w+)\s+CURSOR\s*\((.*?)\)\s+IS\s*.*?\;/gis;
    my ($body) = $cont=~/\b\w+\s+CURSOR\s*.*?\s+IS\s*(.*?)\;/gis;
	my $body2=$body;

	my @prm	= split(/,/, $params);
	for my $pr(@prm)
	{	
	my ($param) = $pr =~ /(\b\w+\b)\s+\b\w+\b/gis;
    $param= $MR->trim($param);
	$body =~ s/($param)/\{$1\}/gis; 	
	}
	$cont = $cur."=(f\"\"\"".$body."\"\"\");";
	#$cont1 =~ s/\Q$body2\E/$body/gis;$MR->log_msg("reached_the_end2 $body");
	
return $cont;
}
sub remove_empty_begin_end
{
	my $cont = shift;
	
	my $index = 0;
	my @flow_positions = ();


	foreach my $member (@$cont)
	{
			
		if ($member =~ /\bBEGIN\b/i)
		{
			push(@flow_positions,{index => $index,key => 'BEGIN'});
			$MR->log_msg("removing_begin______".Dumper($#flow_positions) );
        }
		if ($member =~ /\bEND\b\s*(?!LOOP|IF|CASE)\w*\s*\$*\$*\;/i  )
		{ 
			
			my $last_element = $flow_positions[$#flow_positions];	
			$MR->log_msg("removing_begin2".Dumper($last_element) );
            if ($last_element->{key} eq 'BEGIN')
			{
                @$cont[$last_element->{index}] =~ s/\bBEGIN\b//i;
                @$cont[$index] =~ s/\bEND\b\s*(?!LOOP|IF|CASE)\w*\s*\;//i;
				@$cont[$index] =~ s/\bEND\b\s*(?!LOOP|IF|CASE)\w*\s*\$\$\s*\;//i;
				if(!$IS_PROC){
					pop @flow_positions;
				}
		   
			$MR->log_msg("removing_begin3".Dumper(@$cont[$last_element->{index}]) );}
        
		}
        if ($member =~ /\bEXCEPTION\b/i and $member !~/RAISE/i )
		{
            push(@flow_positions,{index => $index,key => 'EXCEPTION'});
        }
        
		$index += 1;
	}

	return $cont;
}

sub execute_immediate_inside_single_quotes_oracle
{
	my $cont = shift;
	my $cont_string = join("\n", @$cont);
	$cont_string =~ s/execute\s+immediate\s*\(\s*\'(.*)\)/spark.sql("""$1""")/gis;


	$cont_string =~ s/\'\'\'\'/"'"/gis;
	$cont_string =~ s/\'(\s*)\|\|/"""$1+/gis;
	$cont_string =~ s/\|\|(\s*)\'/+$1"""/gis;
	$cont_string =~ s/\"(\s*)\|\|/"$1+/gis;
	$cont_string =~ s/\|\|(\s*)\"/+$1"/gis;
	$cont_string =~ s/(\+\w+)\s*"""\s*\)/$1)/gis;
	#$MR->log_error("zazazaza----".Dumper($cont_string));
	return $cont_string
	#$sql_parser->convert_sql_fragment($cont_string);

}

sub execute_immediate_inside_single_quotes
{
	my $cont = shift;
	my $cont_string = join("\n", @$cont);
	$cont_string =~ s/\'\'(ref.*?)\''/_SINGLE_QUOTE_$1_SINGLE_QUOTE_/gis;
	$cont_string =~ s/execute\s*\'(.*)\'/\nspark.sql(f"""$1""")/gis;  
	$cont_string =~ s/\'\'/"/gis;
	$cont_string =~ s/\'/"""/gis;
	$cont_string =~ s/\"\"\"\s*\|\|/""" +/gis;
	$cont_string =~ s/\|\|\s*\"\"\"/+ """/gis;
	foreach my $arg_def (@{ $Globals::ENV{PRESCAN}->{PROC_ARGS} })
	{
		my $arg=$arg_def->{NAME};
		
		$cont_string =~ s/\"\"\"\s*\+\s*\b\Q$arg\E\b/$arg/gis;
		$cont_string =~ s/\b\Q$arg\E\b\s*\+\s*\"\"\"/$arg/gis;
		$cont_string =~ s/\b\Q$arg\E\b/{$arg}/gis;			
	}
	$cont_string =~ s/_SINGLE_QUOTE_/'/gis;
	
	#return $cont_string
	$sql_parser->convert_sql_fragment("%python".$cont_string);

}
