use strict;
use Globals;
use Data::Dumper;
use Common::MiscRoutines;
use DWSLanguage;
use List::Util qw(first);

no strict 'refs';

my $MR = new Common::MiscRoutines(MESSAGE_PREFIX => 'ORA_HOOKS', DEBUG_FLAG => 1);
my $LAN; # = new DWSLanguage();
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
my $NO_PROCS_OR_FUNCTIONS = 0;

# notebook markdown specs
my $nb_COMMAND_sql     = '-- COMMAND ----------';
my $nb_COMMAND_python  = '# COMMAND ----------';

sub init_oracle_hooks #register this function in the config file
{
	my $param = shift;
	%CFG = %{$param->{CONFIG}};
	$CFG_POINTER = $param->{CONFIG}; #give the ability to modify config incrementally
	$CONVERTER = $param->{CONVERTER};
	$LAN = new DWSLanguage(LOG_FILE_HANDLE => $CONVERTER->{LOG_FILE_HANDLE}) unless $LAN;
	$Globals::ENV{CONVERTER} = $CONVERTER;
	$Globals::ENV{CFG_POINTER} = $CFG_POINTER;
	$Globals::ENV{CONFIG} = $CFG_POINTER;
	#$MR->log_error("CONVERTER: $Globals::ENV{CONVERTER}");
	%USE_VARIABLE_QUOTE = ();

	foreach my $k (keys %$param)
	{
		$MR->log_msg("Init hooks params: $k: $param->{$k}");
	}
	$MR->log_msg("init_oracle_hooks Called. config:\n" . Dumper(\%CFG));

	#Reinitilize vars for when -d option is used:
	$INDENT = 0; #keep track of indents
	%PRESCAN = ();

	if($CFG_POINTER->{catalog_file_path})
	{
		fill_catalog_file($CFG_POINTER->{catalog_file_path});
    }
    
	$Globals::ENV{CONFIG} = $param->{CONFIG};
	# $SRC_TYPE=$Globals::ENV{CONFIG}->{src_type}; 
    
	# $PYTHON_TEMPLATE = $Globals::ENV{CONFIG}->{invoked_python_template_file}; 
	# $FUNCTION_TEMPLATE = $Globals::ENV{CONFIG}->{python_function_template_for_databricks}; 
	# $Globals::ENV{CONFIG}->{FILENAME} = $FILENAME;
	# $PREFIX_TAG = $Globals::ENV{CONFIG}->{prefix_tag};
	# $CURSOR_SUFIX = $Globals::ENV{CONFIG}->{cursor_sufix};
	# $IS_SCRIPT = $Globals::ENV{CONFIG}->{is_script};
	# $SOURCE_FOLDER = $Globals::ENV{CONFIG}->{source_folder};
	# $PROCESS_PACKAGE = $Globals::ENV{CONFIG}->{process_package};
	# $STRIP_EXECUTE = $Globals::ENV{CONFIG}->{strip_execute};
	# $FILE_EXTENSION = $Globals::ENV{CONFIG}->{target_file_extension};
	# $TEMP_VIEW_CREATION_STATEMENT = $Globals::ENV{CONFIG}->{temp_view_creation_statement};
	# $USE_PREFIX = $Globals::ENV{CONFIG}->{use_prefix};
	# $TARGET_CATALOG = $Globals::ENV{CONFIG}->{target_catalog};
	# $INSERT_OVERWRITE = $Globals::ENV{CONFIG}->{insert_overwrite};
	# $INCREMENTAL_WORKLOAD_FOOTER = $Globals::ENV{CONFIG}->{inceremental_footer};
	# $INCREMENTAL_WORKLOAD_HEADER = $Globals::ENV{CONFIG}->{inceremental_header};
	# $TRANSACTION_CONTROL = $Globals::ENV{CONFIG}->{dbt_transaction_control};
	# @CATALOGS = $Globals::ENV{CONFIG}->{catalogs};
	# $sql_parser = new DBCatalog::SQLParser(CONFIG => $Globals::ENV{CONFIG}, DEBUG_FLAG => 0);
}

sub oracle_prescan
{
	my $source_ref = shift;
	my $backup_source_ref = $source_ref;
	$MR->log_msg("Begin oracle_prescan: $source_ref");
	if (ref($source_ref) ne 'ARRAY' && -e $source_ref) #it's a filename
	{
		$MR->log_msg("arg is a filename, reading the file $source_ref");
		my @cont = $MR->read_file_content_as_array($source_ref);
		$MR->log_msg("number of lines read: " . ($#cont+1));
		$source_ref = \@cont;
	}

	# reset per-file data
	if ($Globals::ENV{PRESCAN}->{ALL_VARS})
	{
		foreach my $var_name (keys %{$Globals::ENV{PRESCAN}->{ALL_VARS}})
		{
			delete($Globals::ENV{PRESCAN}->{ALL_VARS}->{$var_name}) if ($Globals::ENV{PRESCAN}->{ALL_VARS}->{$var_name} eq 'LOCAL_VARS');
		}
	}
	$Globals::ENV{PRESCAN}->{$_} = '' foreach qw(PROC_NAME
					    PROC_ARGS
					    PROC_VARS
					    FUNCTION_NAME
					    FUNCTION_ARGS
					    FUNCTION_VARS
					    SCRIPT_TYPE
					    CUSTOM_TYPES
					    LOCAL_VARS
					    );

	my $source_lines = join("\n", @$source_ref);

	#find if there are any conditionals
	my $has_conditionals = 0;
	foreach my $lines (@{$source_ref})
	{
		$has_conditionals = 1 if ($lines =~ /^\s*IF\s+/is);
	}
	$Globals::ENV{PRESCAN}->{NO_CELL_MARKERS} = $has_conditionals;
	$MR->log_error("Removing cell markers from notebook, conditionals found in file: $backup_source_ref") if $has_conditionals;

    $Globals::ENV{CONFIG} = $CFG_POINTER;

	if ($Globals::ENV{CONFIG}->{add_create_for_not_precedure_scripts})
	{
		$source_lines =~ s/\b(function|procedure)\b/ $1/gis;
		$source_lines =~ s/(?<![CREATE|REPLACE])\s+((?:FUNCTION|PROCEDURE)\s+("?\w+"?(?:\."?\w+"?)?)\s*\((.*?)\))/\nCREATE $1/gis;
		$source_lines =~ s/(?<![CREATE|REPLACE])\s+(PROCEDURE\s+("?\w+"?(?:\."?\w+"?)?))/\nCREATE $1/gis;
		$source_lines =~ s/CREATE\s+CREATE/CREATE /gis;
		$source_lines =~ s/REPLACE\s+CREATE/REPLACE /gis;
	}
	
	#	remove all comments
	$source_lines =~ s/\-\-.*$//gim;
	#$source_lines = $sql_parser->remove_c_style_comments($source_lines);

	$MR->log_msg("Begin oracle_prescan3 $source_lines"); 
	$NO_PROCS_OR_FUNCTIONS = 0;
	if ($source_lines =~ /\bCREATE\s+(?:OR\s+REPLACE\s+)?PROCEDURE\s+"?\w+"?(?:\."?\w+"?)?\s*/is)
	{
		prescan_procedure_stmt($source_lines);
	}
	elsif($source_lines =~ /\bCREATE\s+(?:OR\s+REPLACE\s+)?FUNCTION\s+/is)
	{
		prescan_function_stmt($source_lines);
	}
	else
	{
		$MR->log_error("No procs or functions found, writing out SQL file");
		$NO_PROCS_OR_FUNCTIONS = 1;
	}
	my $ret = {PRESCAN_INFO => $Globals::ENV{PRESCAN}};
	$MR->log_msg("PRESCAN inside hook: " . Dumper($ret));
	return $ret;
}

sub prescan_procedure_stmt
{
	my $procedure_stmt = shift;
	$MR->log_msg("Begin prescan_procedure_stmt");
	$MR->log_msg("caught_proc_params: $procedure_stmt");
	my $procedure_name = '';
	my $procedure_args = '';
	my $procedure_vars = '';

	if ($procedure_stmt =~ /\bCREATE\s+(?:OR\s+REPLACE\s+)?PROCEDURE\s+("?\w+"?(?:\."?\w+"?)?)\s*\((.*?)\)\s*\b[AI]S\b(.*?)BEGIN\b/is) # there is no functional difference between IS and AS
	{
		$procedure_name = $1;
		$procedure_args = $2;
		$procedure_vars = $3;
	}
	elsif($procedure_stmt =~ /\bCREATE\s+(?:OR\s+REPLACE\s+)?PROCEDURE\s+("?\w+"?(?:\."?\w+"?)?)\s*\b[AI]S\b(.*?)BEGIN\b/is)
	{
		$procedure_name = $1;
		# no procedure_args
		$procedure_vars = $2;#$MR->log_msg("oracle proc params: $procedure_name");
	}
	
	my ($args_key, $vars_key);
	if ($Globals::ENV{CONFIG}->{change_procedure_to_function})
	{
		$Globals::ENV{PRESCAN}->{FUNCTION_NAME} = $procedure_name;
		$args_key = 'FUNCTION_ARGS';
		$vars_key = 'FUNCTION_VARS';
	}
	else
	{
		$Globals::ENV{PRESCAN}->{PROC_NAME} = $procedure_name;
		$Globals::ENV{PRESCAN}->{SCRIPT_TYPE} = 'PROCEDURE';
		$args_key = 'PROC_ARGS';
		$vars_key = 'PROC_VARS';
	}

	my $prescan_proc_args = ();

	# Save the "before" in case we need to search through it or report it
	$prescan_proc_args->{ORIGINAL_SOURCE} = $procedure_args;

	$MR->log_msg("oracle proc params: $procedure_stmt");
	
	my @arg_defs = split(',', $procedure_args);
	my @var_defs = split(';', $procedure_vars);
	my $arg_num = 0;
	foreach my $arg (@arg_defs)
	{
		$MR->log_msg("oracle proc params: $arg");

		$arg = $MR->trim($arg);
		my $args = {};
		my $last_part = '';
		if($arg =~ /(\w+)\s+(\w+\s+\w+|\w+)\s+(.*)/is)
		{
			$args->{NAME} = $MR->trim($1);     # No longer converting to upper case
			$args->{ARG_TYPE}  = uc($MR->trim($2));
			$last_part = $MR->trim($3);
			
			if ($last_part =~ /(\w+)\s+DEFAULT\s+(.*)/gis)
			{
				$args->{DATA_TYPE} = $1;
				$args->{VALUE} = $2;
			}
			else
			{
				$args->{DATA_TYPE} = $last_part;
			}
			
			#$args->{DATA_TYPE} = uc($MR->trim($3));
			
			#push (@{$Globals::ENV{PRESCAN}->{PROC_ARGS}}, $args);
			#push (@conversion_catalog_add, "stored_procedure_args,$procedure_name,$arg_num" . ':::' . "$1,$2,$3");
			#$arg_num++;
		}
		elsif($arg =~ /(\w+)\s+(\w+)/is)
		{
			
			$args->{NAME} = $MR->trim($1);     # No longer converting to upper case
			$args->{ARG_TYPE} = 'IN';
			$last_part = $MR->trim($2);
			
			$args->{DATA_TYPE} = $last_part;
		}

		my $arg_name = $args->{NAME};
		next unless $arg_name;
		
		$Globals::ENV{PRESCAN}->{$args_key} ||= [];
		push (@{$Globals::ENV{PRESCAN}->{$args_key}}, $args);

		# procedure args are also global vars (declared/defined somewhere else)
## Didn't really turn out that way..
#		$Globals::ENV{PRESCAN}->{GLOBAL_VARS} ||= {};
#		$Globals::ENV{PRESCAN}->{GLOBAL_VARS}->{HASH} ||= {};
#		unless ($Globals::ENV{PRESCAN}->{GLOBAL_VARS}->{HASH}->{$arg_name})
#		{
#			$Globals::ENV{PRESCAN}->{GLOBAL_VARS}->{HASH}->{$arg_name} = 0; #$MR->deep_copy($args);
##			$Globals::ENV{PRESCAN}->{GLOBAL_VARS}->{LIST} ||= [];
##			push (@{$Globals::ENV{PRESCAN}->{GLOBAL_VARS}->{LIST}}, $arg_name);
#		}
		$Globals::ENV{PRESCAN}->{ALL_VARS} ||= {};
		$Globals::ENV{PRESCAN}->{ALL_VARS}->{$arg_name} ||= 'GLOBAL_VARS';
		#push (@conversion_catalog_add, "stored_procedure_args,$procedure_name,$arg_num" . ':::' . "$1,$2,$3");
		$arg_num++;		
	}
	
	my $vars_type = 'LOCAL_VARS';
	if (first { /^\s*[AI]S\b/is } @var_defs) # if we find a second leading IS (or AS) keyword, it means all vars before it were injected globals
	{
		$vars_type = 'GLOBAL_VARS';
	}
	foreach my $var (@var_defs)
	{
		if ($vars_type eq 'GLOBAL_VARS')
		{
			if ($var =~ s/^\s*[AI]S\s+//is) # if we strip off the leading IS/AS keyword, everything from here on is local to the procedure
			{
				$vars_type = 'LOCAL_VARS';
			}
			else
			{
				$MR->log_msg("oracle global vars: $var");
			}
		}
		if ($vars_type eq 'LOCAL_VARS')
		{
			$MR->log_msg("oracle proc vars: $var");
		}
		$var = $MR->trim($var);
		my $vars = {};
		if ($var =~ /^TYPE\s+(\w+)\s+IS\s+(.*)/is) # this defines a custom type, not a single variable
		{
			my ($type_name, $type_def) = ($1, $2);
			if ($type_def =~ /^TABLE\s+OF\s+(\w+)(?:\([^()]+\))?\s+INDEX\s+BY\s+(\w+)(?:\([^()]+\))?$/) # array, possibly associative
			{
				my ($key_type, $val_type) = ($2, $1);
				if ($key_type eq 'INTEGER') # numerically-indexed array
				{
					$type_def = '__EMPTY_ARRAY__()';
				}
				else # anything else requires an associative array, aka hash
				{
					$type_def = '__EMPTY_HASH__()';
				}
			}
			else
			{
				# TODO: hopefully we'll never need to worry about this
			}
			$Globals::ENV{PRESCAN}->{CUSTOM_TYPES}->{$type_name} = $type_def;
			$vars->{NAME} = $type_name;
			$vars->{VALUE} = $vars->{DEFAULT_VALUE} = $type_def;
		}
		elsif ($var =~ /(\w+)\s+(.*)/is)
		{
			$vars->{NAME} = $MR->trim($1);
			my $data_type = $MR->trim($2);
			if($data_type =~ /\s*(.*?)\s*\:\=\s*(.*)/is)
			{
				$vars->{DATA_TYPE} = $data_type = $1;
				my $val = $2;
				
				if ($Globals::ENV{CONFIG}->{change_complex_assignment_to_select})
				{
					if ($val =~/\w+\(/is and $val !~ /(select|insert|Update|delete|alter|drop|merge)/is)
					{
						$val = "SELECT ".$val;
					}
				}
				
				$vars->{VALUE} = $val;
				$vars->{DEFAULT_VALUE} = $val;
			}
			else
			{
				$vars->{DATA_TYPE} = $data_type;
			}
			if (exists($Globals::ENV{PRESCAN}->{CUSTOM_TYPES}) && exists($Globals::ENV{PRESCAN}->{CUSTOM_TYPES}->{$data_type}))
			{
				$vars->{CUSTOM_TYPE} = $Globals::ENV{PRESCAN}->{CUSTOM_TYPES}->{$data_type};
			}
		}

		my $var_name = $vars->{NAME};
		next unless $var_name;
		if ($vars_type eq 'LOCAL_VARS') # globals do not go into the PROC_VARS or FUNCTION_VARS list
		{
			$Globals::ENV{PRESCAN}->{$vars_key} ||= [];
			push (@{$Globals::ENV{PRESCAN}->{$vars_key}}, $vars);
			if ($Globals::ENV{PRESCAN}->{GLOBAL_VARS} && exists($Globals::ENV{PRESCAN}->{GLOBAL_VARS}->{HASH}->{$var_name}))
			{
				$MR->log_error("Local variable matches seen global: $var_name");
			}
		}

		$Globals::ENV{PRESCAN}->{$vars_type} ||= {};
		$Globals::ENV{PRESCAN}->{$vars_type}->{HASH} ||= {};
		unless ($Globals::ENV{PRESCAN}->{$vars_type}->{HASH}->{$var_name})
		{
			$Globals::ENV{PRESCAN}->{$vars_type}->{HASH}->{$var_name} = $MR->deep_copy($vars);
			$Globals::ENV{PRESCAN}->{$vars_type}->{LIST} ||= [];
			push (@{$Globals::ENV{PRESCAN}->{$vars_type}->{LIST}}, $var_name);
		}
		$Globals::ENV{PRESCAN}->{ALL_VARS} ||= {};
		$Globals::ENV{PRESCAN}->{ALL_VARS}->{$var_name} ||= $vars_type;
	}

	$MR->log_msg("PRESCAN STRUCT: " . Dumper($Globals::ENV{PRESCAN}));

	if ($arg_num == 0)
	{
		#push (@conversion_catalog_add, "stored_procedure_args,$procedure_name,x" . ':::');
	}
}

sub prescan_function_stmt 
{
	my $function_stmt = shift;
	$MR->log_msg("Begin prescan_function_stmt: $function_stmt");

	my $function_name = '';
	my $function_args = '';
	my $function_vars = '';
	
	if ($function_stmt =~ /\bCREATE\s+(?:OR\s+REPLACE\s+)?FUNCTION\s+("?\w+"?(?:\."?\w+"?)?)\s*\((.*?)\)\s*RETURN\b.*?\b[AI]S\b(.*?)\bBEGIN\b/is) # there is no functional difference between IS and AS
	{
		$function_name = $MR->trim($1);
		$function_args = $MR->trim($2);
		$function_vars = $MR->trim($3);
	}
	elsif($function_stmt =~ /FUNCTION\s+("?\w+"?(?:\."?\w+"?)?)\s*\((.*?)\)\s*RETURN\b.*?\bIS\b(.*?)\bBEGIN\b/is)
	{
		$function_name = $MR->trim($1);
		$function_args = $MR->trim($2);
		$function_vars = $MR->trim($3);
	}
	
	$Globals::ENV{PRESCAN}->{FUNCTION_NAME} = $function_name;
	$Globals::ENV{PRESCAN}->{SCRIPT_TYPE} = 'FUNCTION';

	my $prescan_function_args = ();

	# Save the "before" in case we need to search through it or report it
	$prescan_function_args->{ORIGINAL_SOURCE} = $function_args;

	$MR->log_msg("oracle function params: $function_args");
	
	my @arg_defs = split(',', $function_args);
	my @var_defs = split(';', $function_vars);
	my $arg_num = 0;
	foreach my $arg (@arg_defs)
	{
		$arg = $MR->trim($arg);
		if($arg =~ /(\w+)\s+(.*)/is)
		{
			my $args = {};
			my $arg_name = $args->{NAME} = $MR->trim($1);     # No longer converting to upper case
			#$args->{ARG_TYPE}  = uc($MR->trim($2));
			my $last_part = $MR->trim($2);
			
			if ($last_part =~ /(\w+)\s+DEFAULT\s+(.*)/gis)
			{
				$args->{DATA_TYPE} = $1;
				$args->{VALUE} = $2;
			}
			else
			{
				$args->{DATA_TYPE} = $last_part;
			}
			
			#$args->{DATA_TYPE} = uc($MR->trim($3));
			
			$Globals::ENV{PRESCAN}->{FUNCTION_ARGS} ||= [];
			push (@{$Globals::ENV{PRESCAN}->{FUNCTION_ARGS}}, $args);

			# function args are also global vars (declared/defined somewhere else)
## Didn't really turn out that way..
#			$Globals::ENV{PRESCAN}->{GLOBAL_VARS} ||= {};
#			$Globals::ENV{PRESCAN}->{GLOBAL_VARS}->{HASH} ||= {};
#			unless ($Globals::ENV{PRESCAN}->{GLOBAL_VARS}->{HASH}->{$arg_name})
#			{
#				$Globals::ENV{PRESCAN}->{GLOBAL_VARS}->{HASH}->{$arg_name} = 0; #$MR->deep_copy($args);
##				$Globals::ENV{PRESCAN}->{GLOBAL_VARS}->{LIST} ||= [];
##				push (@{$Globals::ENV{PRESCAN}->{GLOBAL_VARS}->{LIST}}, $arg_name);
#			}
			$Globals::ENV{PRESCAN}->{ALL_VARS} ||= {};
			$Globals::ENV{PRESCAN}->{ALL_VARS}->{$arg_name} ||= 'GLOBAL_VARS';
			#push (@conversion_catalog_add, "function_args,$function_name,$arg_num" . ':::' . "$1,$2,$3");
			$arg_num++;
		}
	}

	foreach my $var (@var_defs)
	{
		$MR->log_msg("oracle function vars: $var");
		$var = $MR->trim($var);
		if($var =~ /(\w+)\s+(.*)/is)
		{
			my $vars = {};
			my $var_name = $vars->{NAME} = $MR->trim($1);
			my $data_type = $MR->trim($2);
			if($data_type =~ /\s*(.*?)\s*\:\=\s*(.*)/is)
			{
				$vars->{DATA_TYPE} = $1;
				my $val = $2;
				if ($Globals::ENV{CONFIG}->{change_complex_assignment_to_select})
				{
					if ($val =~/\w+\(/is and $val !~ /(select|insert|Update|delete|alter|drop|merge)/is)
					{
						$val = "SELECT ".$val;
					}
				}
				$vars->{VALUE} = $val;
				$vars->{DEFAULT_VALUE} = $val;
			}
			else
			{
				$vars->{DATA_TYPE} = $data_type;
			}

			$Globals::ENV{PRESCAN}->{FUNCTION_VARS} ||= [];
			push (@{$Globals::ENV{PRESCAN}->{FUNCTION_VARS}}, $vars);

			# function vars are local
			$Globals::ENV{PRESCAN}->{LOCAL_VARS} ||= {};
			$Globals::ENV{PRESCAN}->{LOCAL_VARS}->{HASH} ||= {};
			unless ($Globals::ENV{PRESCAN}->{LOCAL_VARS}->{HASH}->{$var_name})
			{
				$Globals::ENV{PRESCAN}->{LOCAL_VARS}->{HASH}->{$var_name} = $MR->deep_copy($vars);
				$Globals::ENV{PRESCAN}->{LOCAL_VARS}->{LIST} ||= [];
				push (@{$Globals::ENV{PRESCAN}->{LOCAL_VARS}->{LIST}}, $var_name);
			}
			$Globals::ENV{PRESCAN}->{ALL_VARS} ||= {};
			$Globals::ENV{PRESCAN}->{ALL_VARS}->{$var_name} ||= 'LOCAL_VARS';
			# TODO: a function var needs to become global when its value is returned
		}
	}

	if ($arg_num == 0)
	{
		#push (@conversion_catalog_add, "functions_args,$function_name,x" . ':::');
	}
}

sub oracle_preprocess
{
	my $cont = shift;
	$MR->log_msg("Starting oracle_preprocess.  Proc name: $Globals::ENV{PRESCAN}->{PROC_NAME}");
	if ($NO_PROCS_OR_FUNCTIONS && !$CFG_POINTER->{_PROCS_OR_FUNCTIONS})
	{
		$MR->log_error("Disabling irrelevant config sections..");
		$CFG_POINTER->{_PROCS_OR_FUNCTIONS} = {};
		# move everything that changes from main config to holder
		foreach (qw(
			    fragment_handling
			    script_header
			    target_file_extension
			    ))
		{
			$CFG_POINTER->{_PROCS_OR_FUNCTIONS}->{$_} = delete $CFG_POINTER->{$_};
		}
		# add new value for anything not completely clobbered
		$CFG_POINTER->{target_file_extension} = 'sql';
		#$Globals::ENV{CONFIG}->{target_file_extension} = 'sql';
	}
	elsif (!$NO_PROCS_OR_FUNCTIONS && (my $restore_cfg = delete $CFG_POINTER->{_PROCS_OR_FUNCTIONS}))
	{
		$MR->log_error("Restoring proc/function config sections..");
		foreach (keys %$restore_cfg)
		{
			$CFG_POINTER->{$_} = delete $restore_cfg->{$_};
		}
	}
	if ($Globals::ENV{PRESCAN}->{PROC_NAME}) #find variable declaration section and remove it.
	{
		my $cont_str = join("\n", @$cont);
		#$MR->log_msg("CONT_STR: $cont_str");
		if ($cont_str =~ /(.*?)(create(?:\s+or\s+replace)?)(\s+procedure\s+)(.*?)\b(is|as)\b(.*?)\bBEGIN\b/isp)
		{
			my ($prematch, $match, $postmatch) = (${^PREMATCH}, ${^MATCH}, ${^POSTMATCH});
			#$cont_str = $1 . $2 . $3 . $4 . $5 . $7 . $postmatch;
			$cont_str = "%PROC_HEADER%;\n" . $postmatch;
			#$MR->log_error("Proc found");
			$MR->log_msg("NEW_CONT_STR: $cont_str");
			my @new_cont = split(/\n/, $cont_str);
			# find and mark the matching procedure end so other block ends will be easier to handle
			foreach (@new_cont)
			{
				if ($_ =~ s@^(\s*END)\s+(\Q$Globals::ENV{PRESCAN}->{PROC_NAME}\E)\s*;\s*$@$1 __P_R_O_C__ $2;@i)
				{
					last; # there will be only one
				}
			}
			@$cont = @new_cont;
		}
	}
	# TODO? ditto for functions?
	if ($Globals::ENV{PRESCAN}->{ALL_VARS}) # find subscripted variables and reformat them
	{
		my $cont_str = join("\n", @$cont);
		my @tokens = $LAN->split_expression_tokens($cont_str);
		my %seen = ();
		for (my $t = 0; $t < $#tokens; $t++) # yes, strictly less-than, because we want to look at rolling pairs
		{
			my $tok = $tokens[$t];
			next unless $tok =~ /\S/;
			my $where;
			if (($where = $Globals::ENV{PRESCAN}->{ALL_VARS}->{$tok}) # current token is a var name
			    && ($tokens[$t + 1] eq '(') # next token could be start of subscript
			    && exists($Globals::ENV{PRESCAN}->{$where}->{HASH}->{$tok}->{CUSTOM_TYPE}) # named var can be subscripted (currently only custom types can)
			    )
			{
				$seen{$tok} ||= 1;
			}
		}
		my @var_names = sort keys %seen;
		if (@var_names)
		{
			my $changed = 0;
			foreach my $var_name (@var_names)
			{
				if ($cont_str =~ s/\b($var_name)\b\((.+?)\)/__S_U_B_S_C_R_I_P_T__($1, $2)/gs)
				{
					$changed++;
				}
			}
			if ($changed)
			{
				@$cont = split(/\n/, $cont_str);
			}
		}
	}
	return @$cont;
}
