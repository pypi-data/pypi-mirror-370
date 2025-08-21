use strict;
# use warnings;
use Globals;
my $MR = new Common::MiscRoutines;
my $LAN = new DWSLanguage();
my %CFG = (); #entries to be initialized
#my $CFG_POINTER = undef;
my $CONVERTER = undef;

my %PRESCAN = ();
my %PRESCAN_INFO = ();

delete $Globals::ENV{PRESCAN};
delete $Globals::ENV{CONFIG};

my $MR = new Common::MiscRoutines(MESSAGE_PREFIX => 'ORA_SRC_HOOKS', DEBUG_FLAG => 1);
#my $CFG_POINTER = undef;
my $sql_parser = new DBCatalog::SQLParser;
my @conversion_catalog_add = ();   # Things that we will add to the conversion catalog

sub init_hooks_oracle
{
	my $p = shift;
	$CONVERTER = $p->{CONVERTER} unless $CONVERTER;
	$CFG_POINTER = $p->{CONFIG};
	$MR->log_msg("init_hooks_oracle. Converter: $CONVERTER, CFG: $CFG_POINTER");
}

sub init_hooks_oracle_with_output_hooks
{
	my $p = shift;
	init_hooks_oracle($p);
	init_output_hooks($p); #calls whatever output hooks initi we have defined
}

sub oracle_preprocess
{
	my $cont = shift;
	$MR->log_msg("Starting oracle_preprocess.  Proc name: $Globals::ENV{PRESCAN}->{PROC_NAME}");
	if ($Globals::ENV{PRESCAN}->{PROC_NAME}) #find variable declaration section and remove it.
	{
		my $cont_str = join("\n", @$cont);
		#$MR->log_msg("CONT_STR: $cont_str");
		if ($cont_str =~ /(.*?)(create|replace)(\s+procedure\s)(.*?)\b(is|as)\b(.*?)\bBEGIN\b/gisp)
		{
			my ($prematch, $match, $postmatch) = (${^PREMATCH}, ${^MATCH}, ${^POSTMATCH});
			$cont_str = $1 . $2 . $3 . $4 . $5 . $7 . $postmatch;
			#$MR->log_error("Proc found");
			$MR->log_msg("NEW_CONT_STR: $cont_str");
			my @new_cont = split(/\n/, $cont_str);
			return @new_cont;
		}
	}
	return @$cont;
}

sub oracle_prescan
{
	my $source_ref = shift;
	$MR->log_msg("Begin oracle_prescan: $source_ref");
	if (ref($source_ref) ne 'ARRAY' && -e $source_ref) #it's a filename
	{
		$MR->log_msg("arg is a filename, reading the file $source_ref");
		my @cont = $MR->read_file_content_as_array($source_ref);
		$MR->log_msg("number of lines read: " . ($#cont+1));
		$source_ref = \@cont;
	}

	$Globals::ENV{PRESCAN}->{PROC_NAME} = '';

	my $source_lines = join("\n", @$source_ref);
	
    $Globals::ENV{CONFIG} = $CFG_POINTER;

	if ($Globals::ENV{CONFIG}->{add_create_for_not_precedure_scripts})
	{
        $source_lines =~ s/(\bfunction\b|\bprocedure\b)/ $1/gis;
		$source_lines =~ s/(?<![CREATE|REPLACE])\s+(\bFUNCTION\s+(\"?\w+\"?\.?\"?\w*\"?)\s*\((.*?)\))/\nCREATE $1/gis;
		$source_lines =~ s/(?<![CREATE|REPLACE])\s+(\bPROCEDURE\s+(\"?\w+\"?\.?\"?\w*\"?)\s*\((.*?)\))/\nCREATE $1/gis;
		$source_lines =~ s/(?<![CREATE|REPLACE])\s+(\bPROCEDURE\s+(\"?\w+\"?\.?\"?\w*\"?))/\nCREATE $1/gis;
		$source_lines =~ s/CREATE\s+CREATE/CREATE $1/gis;
		$source_lines =~ s/REPLACE\s+CREATE/REPLACE /gis;
	}
	
	#	remove all comments
	$source_lines =~ s/\-\-.*$//gim;
	$source_lines = $sql_parser->remove_c_style_comments($source_lines);

	$MR->log_msg("Begin oracle_prescan3 $source_lines"); 
	if ($source_lines =~ /\bCREATE\s+PROCEDURE\s+\"?\w+\"?\.?\"?\w*\"?\s*\(/is or
		$source_lines =~ /\bCREATE\s+OR\b\s+REPLACE\s+PROCEDURE\s+\"?\w+\"?\.?\"?\w*\"?\s*\(/is or
		$source_lines =~ /\bCREATE\s+PROCEDURE\s+\"?\w+\"?\.?\"?\w*\"?\s*/is)
	{
		prescan_procedure_stmt($source_lines);
	}
	elsif($source_lines =~ /\bCREATE\s+FUNCTION\s+/is or $source_lines =~ /\bCREATE\s+OR\b\s+REPLACE\s+FUNCTION\s+/is)
	{
		prescan_function_stmt($source_lines);

	}
	my ($funtion_return_type) = "$source_lines" =~ /\breturn\s+(\w+)\s+AS\b/gis;
	  
	$Globals::ENV{PRESCAN}->{FUNCTION_RETURN_TYPE} = $funtion_return_type;
	my $ret = {PRESCAN_INFO => $Globals::ENV{PRESCAN}};
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

	if ($procedure_stmt =~ /\bCREATE\s+PROCEDURE\s+(\"?\w+\"?\.?\"?\w*\"?)\s*\((.*?)\)\s*\bIS\b(.*?)BEGIN\b/is)
	{
		$procedure_name = $1;
		$procedure_args = $2;
		$procedure_vars = $3;
	}
	elsif($procedure_stmt =~ /\bCREATE\s+OR\b\s+REPLACE\s+PROCEDURE\s+(\"?\w+\"?\.?\"?\w*\"?)\s*\((.*?)\)\s*\bIS\b(.*?)BEGIN\b/is)
	{ 

		$procedure_name = $1;
		$procedure_args = $2;
		$procedure_vars = $3;
	}
	elsif($procedure_stmt =~ /\bCREATE\s+PROCEDURE\s+(\"?\w+\"?\.?\"?\w*\"?)\s*\((.*?)\)\s*\bAS\b(.*?)BEGIN\b/is)
	{
		$procedure_name = $1;
		$procedure_args = $2;
		$procedure_vars = $3;
	}
	elsif($procedure_stmt =~ /\bCREATE\s+OR\b\s+REPLACE\s+PROCEDURE\s+(\"?\w+\"?\.?\"?\w*\"?)\s*\((.*?)\)\s*AS\b(.*?)BEGIN\b/is)
	{
		$procedure_name = $1;
		$procedure_args = $2;
		$procedure_vars = $3;
	}
	elsif($procedure_stmt =~ /\bCREATE\s+OR\b\s+REPLACE\s+PROCEDURE\s+(\"?\w+\"?\.?\"?\w*\"?)\s*\bIS\b(.*?)BEGIN\b/is)
	{
		$procedure_name = $1;
		$procedure_args = $2;
		$procedure_vars = $3;
	}
	elsif($procedure_stmt =~ /\bCREATE\s+OR\b\s+REPLACE\s+PROCEDURE\s+(\"?\w+\"?\.?\"?\w*\"?)\s*AS\b(.*?)BEGIN\b/is)
	{
		$procedure_name = $1;
		$procedure_args = $2;
		$procedure_vars = $3;
	}
	elsif($procedure_stmt =~ /\bCREATE\s+PROCEDURE\s+(\"?\w+\"?\.?\"?\w*\"?)\s*IS\b(.*?)BEGIN\b/is)
	{
		$procedure_name = $1;
		#$procedure_args = $2;
		#$procedure_vars = $3;$MR->log_msg("oracle proc params: $procedure_name");
	}
	elsif($procedure_stmt =~ /\bCREATE\s+PROCEDURE\s+(\"?\w+\"?\.?\"?\w*\"?)\s*AS\b(.*?)BEGIN\b/is)
	{
		$procedure_name = $1;
		#$procedure_args = $2;
		#$procedure_vars = $3;
	}
	
	if ($Globals::ENV{CONFIG}->{change_procedure_to_function})
	{
		$Globals::ENV{PRESCAN}->{FUNCTION_NAME} = $procedure_name;
	}
	else
	{
		$Globals::ENV{PRESCAN}->{PROC_NAME} = $procedure_name;
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
		
		if ($Globals::ENV{CONFIG}->{change_procedure_to_function})
		{
            push (@{$Globals::ENV{PRESCAN}->{FUNCTION_ARGS}}, $args);
        }
        else
		{
			push (@{$Globals::ENV{PRESCAN}->{PROC_ARGS}}, $args);
		}
		push (@conversion_catalog_add, "stored_procedure_args,$procedure_name,$arg_num" . ':::' . "$1,$2,$3");
		$arg_num++;		
	}
	
	foreach my $var (@var_defs)
	{
		$MR->log_msg("oracle proc vars: $var");
		$var = $MR->trim($var);
		if($var =~ /(\w+)\s+(.*)/is)
		{
			my $vars->{NAME} = $MR->trim($1);
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

			if ($Globals::ENV{CONFIG}->{change_procedure_to_function})
			{
				push (@{$Globals::ENV{PRESCAN}->{FUNCTION_VARS}}, $vars);
			}
			else
			{
				push (@{$Globals::ENV{PRESCAN}->{PROC_VARS}}, $vars);
			}			
			
			push (@{$Globals::ENV{PRESCAN}->{VARIABLES}}, $MR->deep_copy($vars));
		}
	}

	$MR->log_msg("PRESCAN STRUCT: " . Dumper($Globals::ENV{PRESCAN}));

	if ($arg_num == 0)
	{
		push (@conversion_catalog_add, "stored_procedure_args,$procedure_name,x" . ':::');
	}
}

sub prescan_function_stmt 
{
	my $function_stmt = shift;
	$MR->log_msg("Begin prescan_function_stmt: $function_stmt");

	my $function_name = '';
	my $function_args = '';
	my $function_vars = '';
	
	if ($function_stmt =~ /\bCREATE\s+FUNCTION\s+(\"?\w+\"?\.?\"?\w*\"?)\s*\((.*?)\)\s*RETURN\b.*?\bIS\b(.*?)\bBEGIN\b\b/is)
	{
		$function_name = $1;
		$function_args = $2;
		$function_vars = $3;
	}
	elsif($function_stmt =~ /\bCREATE\s+OR\b\s+REPLACE\s+FUNCTION\s+(\"?\w+\"?\.?\"?\w*\"?)\s*\((.*?)\)\s*RETURN\b.*?\bIS\b(.*?)\bBEGIN\b/gis)
	{
		$function_name = $MR->trim($1);
		$function_args = $MR->trim($2);
		$function_vars = $MR->trim($3);
		
	}
	elsif($function_stmt =~ /\bCREATE\s+OR\b\s+REPLACE\s+FUNCTION\s+(\"?\w+\"?\.?\"?\w*\"?)\s*\((.*?)\)\s*RETURN\b.*?\bAS\b(.*?)\bBEGIN\b/gis)
	{
		$function_name = $MR->trim($1);
		$function_args = $MR->trim($2);
		$function_vars = $MR->trim($3);
		
	}
	elsif($function_stmt =~ /FUNCTION\s+(\"?\w+\"?\.?\"?\w*\"?)\s*\((.*?)\)\s*RETURN\b.*?\bIS\b(.*?)\bBEGIN\b/gis)
	{
		$function_name = $MR->trim($1);
		$function_args = $MR->trim($2);
		$function_vars = $MR->trim($3);
	}
	
	$Globals::ENV{PRESCAN}->{FUNCTION_NAME} = $function_name;

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
			my $args->{NAME}   = $MR->trim($1);     # No longer converting to upper case
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
			
			push (@{$Globals::ENV{PRESCAN}->{FUNCTION_ARGS}}, $args);
			push (@conversion_catalog_add, "function_args,$function_name,$arg_num" . ':::' . "$1,$2,$3");
			$arg_num++;
		}
	}

	foreach my $var (@var_defs)
	{
		$MR->log_msg("oracle function vars: $var");
		$var = $MR->trim($var);
		if($var =~ /(\w+)\s+(.*)/is)
		{
			my $vars->{NAME} = $MR->trim($1);
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
			push (@{$Globals::ENV{PRESCAN}->{FUNCTION_VARS}}, $vars);
			push (@{$Globals::ENV{PRESCAN}->{VARIABLES}}, $vars);
		}
	}

	if ($arg_num == 0)
	{
		push (@conversion_catalog_add, "functions_args,$function_name,x" . ':::');
	}
}
