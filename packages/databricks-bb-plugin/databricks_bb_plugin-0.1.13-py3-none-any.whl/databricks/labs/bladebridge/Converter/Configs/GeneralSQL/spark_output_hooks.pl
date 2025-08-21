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

my %USE_VARIABLE_QUOTE = ();
my $sql_parser;

my %conv_cat = (); # Conversion catalog

my $sql_case_num = 0;   # Counter for hiding SQL CASE...END

my $global_indent_count = 0;

# For hiding anything (e.g. hiding comments so that we don't perform conversions on them) 
my $hide_num = 0;
my %hide_hash = ();

my $TABLE_CREATED = {};
my $CATALOG = {};
my $comment_header = '';
sub init_spark_hooks #register this function in the config file
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

	$Globals::ENV{CONFIG} = $param->{CONFIG};
	$Globals::ENV{CONFIG}->{FILENAME} = $FILENAME;

	if($Globals::ENV{CONFIG}->{catalog_file_path})
	{
        fill_catalog_file($Globals::ENV{CONFIG}->{catalog_file_path});
    }
    $comment_header = '';
	$sql_parser = new DBCatalog::SQLParser(CONFIG => $Globals::ENV{CONFIG}, DEBUG_FLAG => 0);
}

sub preprocess_for_spark
{
	my $cont = shift; 
	$MR->log_msg("preprocess_for_spark");

	my $modpack = eval('use DWSModulePacking; new DWSModulePacking(IGNORE_DB => 1);');
	$MR->log_msg("reload_modules Eval returned: $@") if $@;
	$modpack->init();

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
	
	my $cont_string = join("\n", @$cont);
	$cont_string = catch_comment_as_header($cont_string);
	if($Globals::ENV{CONFIG}->{remove_comment})
	{
		#	start comment 
		$cont_string =~ s/(\bselect\b\s*)\-\-/$1 _COMMENT_REMOVE_/gis;
		$cont_string =~ s/(\bupdate\b\s*)\-\-/$1 _COMMENT_REMOVE_/gis;
		$cont_string =~ s/(\binsert\b\s*)\-\-/$1 _COMMENT_REMOVE_/gis;
		$cont_string =~ s/(\bdelete\b\s*)\-\-/$1 _COMMENT_REMOVE_/gis;
		$cont_string =~ s/(\,\s*)\-\-/$1 _COMMENT_REMOVE_/gis;
		$cont_string =~ s/^\s*\-\-(.*?$)/# $1;/gim;
		$cont_string =~ s/_COMMENT_REMOVE_/\-\-/gis;
		#	end comment
	}
	
	$cont_string =~ s/^(\s*\\echo.*)/$1;/gim;
	$cont_string =~ s/^(\s*\\set.*)/$1;/gim;
	$cont_string =~ s/\;\s*(\\o.*)/;\n$1;/gim;

	$cont_string =~ s/\s*\=\s*\bANY\s*\(\s*ARRAY\b\s*\[(.*?)\]/ IN ($1/gis;
	
	#$cont_string =~ s/^\s*(\\)/--BB_COMMENT$1/gim;
	
	while($cont_string =~ /\'.*?\-.*?\'/gim)
	{
        $cont_string =~ s/\'(.*?)\-(.*?)\'/'$1_$2'/gim;
    }
    
	
	#$cont_string =~ /(\w*[^[:ascii:]]\w*)/gim;
	#$MR->log_error($1);
	#
	$cont_string =~ s/\;\s+DELETE/;\nDELETE/gis;
	$cont_string =~ s/\bCREATE\s+PROJECTION\b/CREATE_PROJECTION/gis;
	$cont_string =~ s/(\w*[^\x00-\x7F]\w*)/`$1`/gisu;

	my @temp_tables = sort {length($b) <=> length($a)} keys %{$Globals::ENV{PRESCAN}->{TEMP_TABLES}};
	
	foreach my $var (@temp_tables)
	{
		my $var_value = $Globals::ENV{PRESCAN}->{TEMP_TABLES}->{$var};
        
		$cont_string =~ s/$var_value/{$var}/gis;
		$cont_string =~ s/\bFROM\s+\{$var\}/FROM $var/gis;
		$cont_string =~ s/\bJOIN\s+\{$var\}/JOIN $var/gis;
		#$cont_string =~ s/\bTABLE\s+\{$var\}/TABLE $var/gis;
	}
	
	my @cmnts = $cont_string =~/(?<![\"])\/\*.*?\*\//gis;
	for my $cm(@cmnts)
	{
		my $copied_cm = $cm;
		$cm =~ s/\;//gis;
		$cont_string =~ s/\Q$copied_cm\E/$cm/gis;
	}
	
	if ($Globals::ENV{CONFIG}->{last_temp_select})
	{
        $cont_string .= $Globals::ENV{CONFIG}->{last_temp_select};
    }
    
	foreach my $var (keys %{$Globals::ENV{PRESCAN}->{WIDGETS}})
	{
		$cont_string =~ s/\$\{hiveconf\:$var\}/{$var}/gis;
	}
	
	@$cont = split(/\n/, $cont_string);
	return @$cont;
}

sub preprocess_for_spark_with_temp_tables
{
	my $cont = shift;
	$MR->log_msg("preprocess_for_spark_with_temp_tables");

	my $modpack = eval('use DWSModulePacking; new DWSModulePacking(IGNORE_DB => 1);');
	$MR->log_msg("reload_modules Eval returned: $@") if $@;
	$modpack->init();

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

	my $cont_string = join("\n", @$cont);
	$cont_string = catch_comment_as_header($cont_string);
	if($Globals::ENV{CONFIG}->{remove_comment})
	{
		#	start comment
		$cont_string =~ s/(\bselect\b\s*)\-\-/$1 _COMMENT_REMOVE_/gis;
		$cont_string =~ s/(\bupdate\b\s*)\-\-/$1 _COMMENT_REMOVE_/gis;
		$cont_string =~ s/(\binsert\b\s*)\-\-/$1 _COMMENT_REMOVE_/gis;
		$cont_string =~ s/(\bdelete\b\s*)\-\-/$1 _COMMENT_REMOVE_/gis;
		$cont_string =~ s/(\,\s*)\-\-/$1 _COMMENT_REMOVE_/gis;
 		$cont_string =~ s/^\s*\-\-(\w+\n*\s*\w+\s+JOIN)/COMMENT_BEFORE_JOIN $1/gim; 	# used for one type of intra-dml comments
		# $cont_string =~ s/^\s*\-\-(.*?$)/# $1/gim;										# general case, used for all comments
		$cont_string =~ s/COMMENT_BEFORE_JOIN/\-\-/gis;#
		$cont_string =~ s/_COMMENT_REMOVE_/\-\-/gis;
		#	end comment
	}

	$cont_string =~ s/^(\s*\\echo.*)/$1;/gim;
	$cont_string =~ s/^(\s*\\set.*)/$1;/gim;
	$cont_string =~ s/\;\s*(\\o.*)/;\n$1;/gim;

	$cont_string =~ s/\s*\=\s*\bANY\s*\(\s*ARRAY\b\s*\[(.*?)\]/ IN ($1/gis;

	#$cont_string =~ s/^\s*(\\)/--BB_COMMENT$1/gim;

	# while($cont_string =~ /\'.*?\-.*?\'/gim)
	# {
    #     $cont_string =~ s/\'(.*?)\-(.*?)\'/'$1_$2'/gim;
    # }

	#$cont_string =~ /(\w*[^[:ascii:]]\w*)/gim;
	#$MR->log_error($1);
	#
	$cont_string =~ s/\;\s+DELETE/;\nDELETE/gis;
	$cont_string =~ s/\bCREATE\s+PROJECTION\b/CREATE_PROJECTION/gis;
	$cont_string =~ s/(\w*[^\x00-\x7F]\w*)/`$1`/gisu;

	$cont_string =~ s/(\s+\bCREATE\s+VIEW\b)/;\n\n$1/gisu;

	my @temp_tables = sort {length($b) <=> length($a)} keys %{$Globals::ENV{PRESCAN}->{TEMP_TABLES}};

	foreach my $var (@temp_tables)
	{
		# my $var_value = $Globals::ENV{PRESCAN}->{TEMP_TABLES}->{$var};
		# $cont_string =~ s/$var_value/{$var}/gis;

		$cont_string =~ s/\bFROM\s+\{$var\}/FROM $var/gis;
		$cont_string =~ s/\bJOIN\s+\{$var\}/JOIN $var/gis;
		#$cont_string =~ s/\bTABLE\s+\{$var\}/TABLE $var/gis;
	}

	my @cmnts = $cont_string =~/(?<![\"])\/\*.*?\*\//gis;
	for my $cm(@cmnts)
	{
		my $copied_cm = $cm;
		$cm =~ s/\;//gis;
		$cont_string =~ s/\Q$copied_cm\E/$cm/gis;
	}

	if ($Globals::ENV{CONFIG}->{last_temp_select})
	{
        $cont_string .= $Globals::ENV{CONFIG}->{last_temp_select};
    }

	foreach my $var (keys %{$Globals::ENV{PRESCAN}->{WIDGETS}})
	{
		$cont_string =~ s/\$\{hiveconf\:$var\}/{$var}/gis;
		$cont_string =~ s/\$\{hivevar\:$var\}/{$var}/gis;
	}

	$cont_string =~ s/TRUNCATE\s+TABLE.*?\.M_\w+\s*\;\s+INSERT\s+INTO/INSERT_INTO_M_OVERWRITE/gis;
	$cont_string =~ s/ALTER\s+TABLE.*?\.M_\w+.*?\;\s+INSERT\s+INTO/INSERT_INTO_M_OVERWRITE/gis;

	@$cont = split(/\n/, $cont_string);
	return @$cont;
}

sub catch_comment_as_header
{
	my $cont = shift;
	
	my $ret_cont = '';
	my $is_body = 0;
	my $header_started = 0;
	$comment_header = '';
	foreach my $ln (split(/\n/, $cont))
	{
		
		if ($is_body)
		{
            $ret_cont .= $ln. "\n";
			next;
        }
		
		if (!$ln)
		{
			if ($header_started)
			{
                $is_body = 1;
            }
			next;
		}

		if ($ln =~ /^\s+/)
		{
			$header_started = 1;
            $comment_header .= $ln."\n";
        }
        elsif($ln =~ /^\s*\-/)
		{
			$header_started = 1;
			$comment_header .= $ln."\n";
		}
		else
		{
			$is_body = 1;
			$ret_cont .= $ln. "\n";
		}
	}
	$comment_header .= "\n";
	$comment_header =~ s/\-\-/#/gm;
	return $ret_cont;
}

sub create_temp_table_handler
{
	my $ar = shift;
	my $cont = join("\n", @$ar);
	$MR->log_msg("create_temp_table_handler: $cont");
	$cont = $MR->trim($cont);
	$cont =~ s/\)\s*STORED\s+AS.*/)/gis;
	$cont =~/\bCREATE\b\s+TEMPORARY\s+TABLE\s*\{?(.*?)\}?\s*\((.*)\)/gis;
	my $tbl_name = $MR->trim($1);
	my $data = $MR->trim($2);
	$data =~ s/\(.*?\)//g;
	my $ret_str = columns_to_spark($tbl_name,$data);
	
	my $create_temp_view_template = $Globals::ENV{CONFIG}->{commands}->{CREATE_TEMP_VIEW};
	$create_temp_view_template =~ s/\%TABLE\%/$tbl_name/gis;
	$ret_str .= $create_temp_view_template;
	
	return $ret_str;
}

sub delete_partition_handler
{
	my $ar = shift;
	my $cont = join("\n", @$ar);
	$MR->log_msg("delete_partition_handler: $cont");
	$cont = $MR->trim($cont);
	my $delete_partition_template = $Globals::ENV{CONFIG}->{commands}->{DELETE_PARTITION};
	my $table;
	my $condition;

	if($cont =~ /\bALTER\s+TABLE\s*(.*?)\s+DROP\b.*?EXISTS\s+PARTITION\s*\((.*)\)/gis)
	{
		$table = $1;
		$condition = $2;
	}
	elsif($cont =~ /\bALTER\s+TABLE\s*(.*?)\s+DROP\b.*?\s+PARTITION\s*\((.*)\)/gis)
	{
		$table = $1;
		$condition = $2;		
	}
	if ($Globals::ENV{CONFIG}->{replace_comma_to_AND_in_Delete})
	{
        $condition =~ s/\,/ AND /gis;
    }
    
	$delete_partition_template =~ s/\%TABLE\%/$table/gis;
	$delete_partition_template =~ s/\%CONDITION\%/$condition/gis;
	$cont = $CONVERTER->convert_sql_fragment($cont);
	my $swap = $Globals::ENV{CONFIG}->{commands}->{SWAP};
	$swap =~ s/\%QUERY\%/$delete_partition_template/gis;
	
	return $swap;	
}

sub truncate_table_handler
{
	my $ar = shift;
	my $cont = join("\n", @$ar);
	$MR->log_msg("truncate_table_handler: $cont");
	my $swap = $Globals::ENV{CONFIG}->{commands}->{SWAP};
	$swap =~ s/\%QUERY\%/$cont/gis;
	
	return $swap;
}

sub columns_to_spark
{
	my $tbl_name = shift;
	my $data = shift;

	my $ret_str = '';
	
	$data =~ s/\(.*?\)//gim;
	my $cols = '';
	foreach my $col (split(',',$data))
	{
		$col = $MR->trim($col);
		if ($cols ne '')
		{
			$cols .= ",";
		}
		my $column_template = $Globals::ENV{CONFIG}->{commands}->{COLUMN};
		$col =~ /(\w+)/;
		$col = $1;
		$column_template =~ s/\%COLUMN_NAME\%/$col/gis;
		$cols .= $column_template;
	}
	my $create_table_template = $Globals::ENV{CONFIG}->{commands}->{CREATE_TABLE_TEMPLATE};
	$create_table_template =~ s/\%COLUMNS\%/$cols/gis;
	$create_table_template =~ s/\%TABLE\%/$tbl_name/gis;
	$ret_str = $create_table_template;

	return $ret_str;	
}

sub insert_handler
{
	my $ar = shift;

	my $cont = join("\n", @$ar);
	$MR->log_msg("insert_handler: $cont");
	$cont = $MR->trim($cont);
	my $ret_str = '';
	
	$cont =~ s/\bINSERT\s+INTO\b\s+TABLE\b/INSERT INTO/gis;
	#$cont =~ s/\bPARTITION\s+\(.*?\)//gis;
	
		
	$cont =~ /\bINSERT\s+INTO\b\s*\w*\s+\$*\{?(\w+\:*\w*\}?\w*\.?\w*\.?\w*)\}?\s*\(*\s*(.*?)\)*\s*(SELECT.*)\;?/gis;
	
	my $tbl_name = $1;
	my $columns = $2;
	my $select = $3;

	$tbl_name =~ s/\{//gis;
	$tbl_name =~ s/\}//gis;
	#if(!$tbl_name)
	#{
	#	return $cont;
	#}
	if ($Globals::ENV{PRESCAN}->{TEMP_TABLES}->{$tbl_name})
	{
		if (!$TABLE_CREATED->{$tbl_name})
		{
            my $create_table_template = $Globals::ENV{CONFIG}->{commands}->{CREATE_TABLE_TEMPLATE};
			$create_table_template =~ s/\%QUERY\%/$select/gis;
			$create_table_template =~ s/\%TABLE\%/$tbl_name/gis;
			$ret_str .= $create_table_template;
			$TABLE_CREATED->{$tbl_name} = 1;
		}
        else
		{
			$ret_str = columns_to_spark($tbl_name,$columns);
			
			my $create_sub_table_template = $Globals::ENV{CONFIG}->{commands}->{CREATE_SUB_TABLE};
			$create_sub_table_template =~ s/\%QUERY\%/$select/gis;
			$create_sub_table_template =~ s/\%TABLE\%/$tbl_name/gis;
			$ret_str .= $create_sub_table_template;
		}

		my $create_temp_view_template  = $Globals::ENV{CONFIG}->{commands}->{CREATE_TEMP_VIEW};
		$create_temp_view_template =~ s/\%TABLE\%/$tbl_name/gis;
		$ret_str .= $create_temp_view_template;			
    }
    else
	{
		my $swap  = $Globals::ENV{CONFIG}->{commands}->{SWAP};
		$cont = $CONVERTER->convert_sql_fragment($cont);
		$cont =~ s/\;\s*$//gis;  # remove last ;
		$swap =~ s/\%QUERY\%/$cont/gis;
		$ret_str .= $swap;
	}

	# checking if the ORDER BY CLAUSE is already present, if not, then we add it
	my $order_by = $ret_str =~ /PARTITION\s+BY[^\)]+ORDER\s+BY\s+/gis;
	if (!($order_by))
	{
		$ret_str =~ s/(ROW_NUMBER\(\)\sOVER\s\(PARTITION\s+BY\s+[\w\.]+)\)/$1 ORDER BY 1)/gis;
		$ret_str =~ s/(ROW_NUMBER\(\)\sOVER\s*\(PARTITION\s+BY\s+[\w\.\{\}\'\$\,\s]+)\)/$1 ORDER BY 1)/gis;
		$ret_str =~ s/(ROW_NUMBER\(\)\sOVER\s*\()\)/$1ORDER BY 1)/gis;
		$ret_str =~ s/ORDER\s+BY\s+1\s+ORDER\s+BY\s+1/ORDER BY 1/gis;
	}
	return $ret_str;
}

sub insert_into_M_handler
{
	my $ar = shift;

	my $cont = join("\n", @$ar);
	$MR->log_msg("insert_into_M_handler: $cont");
	$cont = $MR->trim($cont);
	my $ret_str = $Globals::ENV{CONFIG}->{commands}->{SET_PARTITION_OVERWRITE_MODE};

	$cont =~ /\bINSERT_INTO_M_OVERWRITE\b\s*\w*\s+\$*\{?(\w+\:*\w*\}?\w*\.?\w*\.?\w*)/gis;
	$cont =~ s/\bINSERT_INTO_M_OVERWRITE\b/INSERT OVERWRITE/gis;

	my $tbl_name = $1;

	$tbl_name =~ s/\{//gis;
	$tbl_name =~ s/\}//gis;
	#if(!$tbl_name)
	#{
	#	return $cont;
	#}
	if ($Globals::ENV{PRESCAN}->{TEMP_TABLES}->{$tbl_name})
	{
        $self->log_error('$Globals::ENV{PRESCAN}->{TEMP_TABLES}->{$tbl_name} is defined, see insert_handler subroutine from this hooks');
    }
    else
	{
		my $swap  = $Globals::ENV{CONFIG}->{commands}->{SWAP};
		$cont = $CONVERTER->convert_sql_fragment($cont);
		$swap =~ s/\%QUERY\%/$cont/gis;
		$ret_str .= $swap;
	}
	return $ret_str;
}

sub insert_overwrite_table
{
	my $ar = shift;
	$MR->log_msg("insert_overwrite_table:");
	my $cont = join("\n", @$ar);

	$cont = $MR->trim($cont);
	my $ret_str = '';
	
#	$cont =~ /\bINSERT\s+OVERWRITE\s+TABLE\b\s+\{?(\w+\}?\w*\.?\w*\.?\w*)\}?\s*\(\s*(.*?)\)\s+/gis;
#	
#	my $tbl_name = $1;
#
#	$tbl_name =~ s/\{//gis;
#	$tbl_name =~ s/\}//gis;
#
#	if ($Globals::ENV{PRESCAN}->{TEMP_TABLES}->{$tbl_name})
#	{
#		if (!$TABLE_CREATED->{$tbl_name})
#		{
#            my $create_table_template = $Globals::ENV{CONFIG}->{commands}->{CREATE_TABLE_TEMPLATE};
#			$create_table_template =~ s/\%QUERY\%/$select/gis;
#			$create_table_template =~ s/\%TABLE\%/$tbl_name/gis;
#			$ret_str .= $create_table_template;
#		}
#        else
#		{
#			$TABLE_CREATED->{$tbl_name} = 1;
#
#			$ret_str = columns_to_spark($tbl_name,$columns);
#			
#			my $create_sub_table_template = $Globals::ENV{CONFIG}->{commands}->{CREATE_SUB_TABLE};
#			$create_sub_table_template =~ s/\%QUERY\%/$select/gis;
#			$create_sub_table_template =~ s/\%TABLE\%/$tbl_name/gis;
#			$ret_str .= $create_sub_table_template;
#		}
#
#		my $create_temp_view_template  = $Globals::ENV{CONFIG}->{commands}->{CREATE_TEMP_VIEW};
#		$create_temp_view_template =~ s/\%TABLE\%/$tbl_name/gis;
#		$ret_str .= $create_temp_view_template;			
#    }
#    else
#	{
	my $swap  = $Globals::ENV{CONFIG}->{commands}->{SWAP};
	$cont = $CONVERTER->convert_sql_fragment($cont);
	$swap =~ s/\%QUERY\%/$cont/gis;
	$ret_str .= $swap;
	#}

	return $ret_str;
}

sub create_temporary_table_as_parquet_handler
{
	my $ar = shift;
	$MR->log_msg("create_temporary_table_as_parquet_handler:");
	my $cont = join("\n", @$ar);
	
	$cont = $MR->trim($cont);

	$cont =~ /create\s+temporary\s+table(.*?)\bSTORED\s+AS\s+PARQUET\b.*?(select.*)/gis;

	my $tbl_name = $MR->trim($1);
	my $select = $2;

	$tbl_name =~ s/\{//gis;
	$tbl_name =~ s/\}//gis;
			
	my $ret_str = '';

	my $create_table_template = $Globals::ENV{CONFIG}->{commands}->{CREATE_TABLE_TEMPLATE};
	$create_table_template =~ s/\%QUERY\%/$select/gis;
	$create_table_template =~ s/\%TABLE\%/$tbl_name/gis;
	$ret_str .= $create_table_template;
	$TABLE_CREATED->{$tbl_name} = 1;
	
	my $create_temp_view_template = $Globals::ENV{CONFIG}->{commands}->{CREATE_TEMP_VIEW};
	$create_temp_view_template =~ s/\%TABLE\%/$tbl_name/gis;
	$ret_str .= "\n".$create_temp_view_template;			
	return $ret_str;
}

sub default_wrap_sparksql_handler
{
	my $ar = shift;
	#return '' if $STOP_OUTPUT;
	my $cont = join("\n", @$ar);
	$MR->log_msg("default_wrap_sparksql_handler: $cont");

	$cont =~ s/^\n//;
	my $ret = '';

	$ret = $CONVERTER->convert_sql_fragment($cont);

	return "spark.sql(f\"\"\"" . $ret . "\"\"\")";
}

sub create_table_as_parquet_handler
{
	my $ar = shift;
	$MR->log_msg("create_table_as_parquet_handler:");
	my $cont = join("\n", @$ar);
	
	$cont = $MR->trim($cont);

	# Enhanced regex to support optional 'temporary' keyword, stricter table name capture,
	# and flexible 'LOCATION' path formats (quoted or unquoted).

	# $cont =~ /create[\w\s]+table(.*?)(\(.*?)\s+\bSTORED\s+AS\s+PARQUET\b(\s+LOCATION.*)/gis;
	$cont =~ /create\s+(temporary\s+)?table\s+([^(\s]+)\s+(STORED\s+AS\s+PARQUET\b)(?:\s+LOCATION\s+(?:'(.*?)'|(\S+)))?/gis;

	my $tbl_name = $MR->trim($2);
	my $columns = $3;
	my $locations = $4;

	#$tbl_name =~ s/\{//gis;
	#$tbl_name =~ s/\}//gis;

	$locations =~ s/'\//'/gis;
	$locations =~ s/"\//"/gis;
	$locations =~ s/'\s*\;/';/gis;
	$locations =~ s/"\s*\;/";/gis;
			
	my $parquet_create_table = $MR->deep_copy($Globals::ENV{CONFIG}->{commands}->{PARQUET_CREATE_TABLE});
	my $ret_value = '';

	my $count = 0;
	foreach my $template (@$parquet_create_table)
	{
		$template =~ s/\%TABLE\%/$tbl_name/gis;
		$template =~ s/\%COLUMNS\%/$columns/gis;
		$template =~ s/\n\%LOCATION\%/$locations;/gis;		
		my $create_temp_view_template = $Globals::ENV{CONFIG}->{commands}->{SWAP};
		$create_temp_view_template = $Globals::ENV{CONFIG}->{commands}->{SWAP_NOTEBOOK} if exists $Globals::ENV{CONFIG}->{commands}->{SWAP_NOTEBOOK}
			&& $Globals::ENV{CONFIG}->{commands}->{SWAP_NOTEBOOK} && $count eq 0;
		$create_temp_view_template =~ s/\%QUERY\%/$template/gis;
		$ret_value .= $create_temp_view_template;
		$count++;
	}

	$TABLE_CREATED->{$tbl_name} = 1;
	
	return $ret_value;
}

sub with_handler
{
	my $ar = shift;
	#return '' if $STOP_OUTPUT;
	my $cont = join("\n", @$ar);
	$MR->log_msg("with_handler: $cont");
	
	$cont = $MR->trim($cont);
	$cont =~ /\bINSERT\s+INTO\b\s+\{?(\w+\}?\w*\.?\w*\.?\w*)\}?\s*\(\s*(.*?)\)\s*/gis;
	
	my $tbl_name = $MR->trim($1);
	$tbl_name =~ s/\{//gis;
	$tbl_name =~ s/\}//gis;

	#conditional to keep backwards compatibility
	$cont =~ s/\bINSERT\s+INTO\b.*?\(//gis unless $Globals::ENV{CONFIG}->{keep_insert_into_for_with_statements};
	my $create_table_for_with = $Globals::ENV{CONFIG}->{commands}->{CREATE_TABLE_FOR_WITH};
	$create_table_for_with =~ s/\%TABLE\%/$tbl_name/gis;
	$create_table_for_with =~ s/\%QUERY\%/$cont/gis;
	my $ret_str = $create_table_for_with;
	my $create_temp_view_template  = $Globals::ENV{CONFIG}->{commands}->{CREATE_TEMP_VIEW};
	$create_temp_view_template =~ s/\%TABLE\%/$tbl_name/gis;
	$ret_str .= $create_temp_view_template;			
	
	return $ret_str;
}

sub comment_handler
{
	my $ar = shift;
	#return '' if $STOP_OUTPUT;
	my $cont = join("\n", @$ar);
	$MR->log_msg("comment_handler: $cont");
	
	$cont =~ s/^\s*\#(.*);/#$1/g;
	$cont =~ s/^\s*\-\-(.*)/#$1/g;
	
	return $cont;
}

sub spark_default_handler
{
	my $ar = shift;
	#return '' if $STOP_OUTPUT;
	my $sql = join("\n", @$ar);
	$MR->log_msg("spark_default_handler: $sql");
	#$sql = convert_dml($ar);
	#
	#$sql = adjust_statement($sql);

	return '';
}



sub widget_generation
{
	my $widget_declare = "\n\#widget initializations\n";
	my $widget_assignment = "\#widget assignment\n";
	
	foreach my $var (keys %{$Globals::ENV{PRESCAN}->{WIDGETS}})
	{
		my $widget_template = $Globals::ENV{CONFIG}->{commands}->{WIDGET_DECLARE};
		$widget_template =~ s/\%VAR_NAME\%/$var/gis;
		if ($CATALOG->{$var})
		{
			my $val = (keys %{$CATALOG->{$var}})[0];
			$widget_template =~ s/\%VALUE\%/$val/gis;
        }
		else
		{
			$widget_template =~ s/\%VALUE\%/$var/gis;
		}
		$widget_declare .= $widget_template;
		
		my $widget_assignment_template = $Globals::ENV{CONFIG}->{commands}->{WIDGET_ASSIGNMENT};
		$widget_assignment_template =~ s/\%VAR_NAME\%/$var/gis;
      
		$widget_assignment .= $widget_assignment_template;
	}
	
	return "$widget_declare\n$widget_assignment\n\n";
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

	$str =~ s/^\s*\-\-.*$//gim;
	$str =~ s/\/\*.*?\*\///gis;
	
	my $table_name;
	my @insert_columns = ();
	my %hashed_insert_columns = ();

	$str =~ s/INSERT\s*\/\*.*?\*\/\s*INTO\s+/INSERT INTO /gis;
	#	with section
	if ($str =~ /INSERT\s+INTO\s+(\w+\.?\w*\.?\w*)\s+SELECT(.*?)\bFROM\b/gis)
	{
        $table_name = uc($1);
		my $column_count = get_columns_count_from_select($2);

		if (!$CATALOG->{$table_name} or $column_count == -1)
		{
			return $CONVERTER->convert_sql_fragment($str);
		}

		my @insert_columns_count = (1..scalar(keys %{$CATALOG->{$table_name}}) - $column_count);
		foreach(@insert_columns_count)
		{
			$missed_select_columns .= ", null\n";
		}
		$str =~ s/(INSERT\s+INTO\s+(\w+\.?\w*\.?\w*)\s+SELECT.*?)\bFROM\b/$1$missed_select_columns FROM/gis;
	}
	elsif ($str =~ /INSERT\s+INTO\s+(\w+\.?\w*\.?\w*)\s*\(SELECT(.*?)\bFROM\b/gis)
	{
        $table_name = uc($1);
		my $column_count = get_columns_count_from_select($2);

		if (!$CATALOG->{$table_name} or $column_count == -1)
		{
			return $CONVERTER->convert_sql_fragment($str);
		}

		my @insert_columns_count = (1..scalar(keys %{$CATALOG->{$table_name}}) - $column_count);
		foreach(@insert_columns_count)
		{
			$missed_select_columns .= ", null\n";
		}
		$str =~ s/(INSERT\s+INTO\s+(\w+\.?\w*\.?\w*)\s*\(\s*SELECT.*?)\bFROM\b/$1$missed_select_columns FROM/gis;
	}
	elsif ($str =~ /INSERT\s+INTO\s+(\w+\.?\w*\.?\w*)\s+\((.*?)\)\s*\(?\s*SELECT.*?\bFROM\b/gis)
	{
        $table_name = uc($1);

        @insert_columns = split(/\,/, $2);
		%hashed_insert_columns = map {uc($MR->trim($_)) => 1} @insert_columns;
		if (!$CATALOG->{$table_name})
		{
			return $CONVERTER->convert_sql_fragment($str);
		}
	
		foreach my $col (keys %{$CATALOG->{$table_name}})
		{
			$col = $MR->trim($col);
			if (!$hashed_insert_columns{$col})
			{
				$missed_insert_columns .= ", $col\n";
				$missed_select_columns .= ", null\n";
			}
		}
		$str =~ s/(INSERT\s+INTO\s+\w+\.?\w*\.?\w*\s+\(.*?)(\)\s*\(?\s*SELECT.*?)\bFROM\b/$1$missed_insert_columns$2$missed_select_columns FROM/gis;
	}
	elsif ($str =~ /\bINSERT\s+INTO\s+(\w+\.?\w*\.?\w*)\s+WITH\s+.*?\bSELECT.*?\)\s*SELECT(.*?)\bFROM\b/gis)
	{
        $table_name = uc($1);
		my $column_count = get_columns_count_from_select($2);

		if (!$CATALOG->{$table_name} or $column_count == -1)
		{
			return $CONVERTER->convert_sql_fragment($str);
		}
		
		my @insert_columns_count = (1..scalar(keys %{$CATALOG->{$table_name}}) - $column_count);
		foreach(@insert_columns_count)
		{
			$missed_select_columns .= ", null\n";
		}

		$str =~ s/(\bINSERT\s+INTO\s+\w+\.?\w*\.?\w*\s+WITH\s+.*?\bSELECT.*?\)\s*SELECT.*?)\bFROM\b/$1$missed_select_columns FROM/gis;
	}
    $MR->log_msg("Pre Output insert_with_select: $str");

	$str = $CONVERTER->convert_sql_fragment($str);
   
    $MR->log_msg("Output insert_with_select: $str");
	return $str;
}

sub echo_handler
{
	my $ar = shift;
	#return '' if $STOP_OUTPUT;
	my $cont = join("\n", @$ar);
	$MR->log_msg("echo_handler: $cont");
	$cont =~ s/\\echo//gis;
	$cont =~ s/\;//gis;
	$cont =~ s/\`\"/`,"/gis;
	$cont =~ s/\+\%/","%/gis;
	$cont =~ s/\`/"/gis;
	if ($cont =~ /\"(\%.*?)\"/gis)
	{
        my $format_pattern = $1;
		$format_pattern =~ s/Y/y/g;
		$format_pattern =~ s/\%//g;
		my $date_to_string = $Globals::ENV{CONFIG}->{commands}->{DATE_TO_STRING};
		$date_to_string =~ s/\%PATTERN\%/$format_pattern/gis;
		#my $new_val = "cast(date_format(current_timestamp,'$format_pattern') as string)";
		$cont =~ s/\"\%.*?\"/$date_to_string/gis;
		$cont = "concat($cont)";
    }
    else
	{
		$cont = "'$cont'";
	}
	return "SELECT(printf($cont));";
}

sub create_external_table
{
	my $ar = shift;
	#return '' if $STOP_OUTPUT;
	my $cont = join("\n", @$ar);
	$MR->log_msg("create_external_table: $cont");
	$cont =~ s/CREATE\s*EXTERNAL\s+TABLE/CREATE OR REPLACE TABLE/gis,
	$cont =~ s/CREATE\s+MANAGED\s+EXTERNAL\s+TABLE/CREATE OR REPLACE TABLE/gis,
	$cont =~ s/(.*?)\s*\bAS\s+COPY\s+FROM\b.*/$1;/gis,
	$cont = $CONVERTER->convert_sql_fragment($cont);
	return $cont;
}

sub create_projection
{
	my $ar = shift;
	#return '' if $STOP_OUTPUT;
	#my $cont = join("\n", @$ar);
	#$MR->log_msg("create_view: $cont");
	#$cont =~ s/\bCREATE\s+PROJECTION\b/CREATE OR REPLACE VIEW/gis,
	#$cont =~ s/\bSEGMENTED\s+BY\s+hash\s*\(.*/;/gis,
	#$cont =~ s/\bUNSEGMENTED\s+ALL\s+NODES\b//gis;
	#$cont =~ s/\/\*\+/\/* +/gis;
	
	#$cont = $CONVERTER->convert_sql_fragment($cont);
	return '';	
}

sub delete_multi_where_condition
{
	my $ar = shift;
	my $cont = join("\n", @$ar);
	$MR->log_msg("delete_multi_where_condition: $cont");
	$cont =~ /(delete.*?from.*?where\s*)\((.*?)\)\s*in\s*\((\s*SELECT\s*.*)\)/gis;
	my $delete_first_part = $MR->trim($1);
	my @delete_columns = split /\,/,$MR->trim($2);
	my $delete_select = $MR->trim($3);
	
	$delete_select =~ /(SELECT\s*)(.*?)(from.*)/gis;
	my $dl_select_first_part = $MR->trim($1);
	my @dl_select_columns = split /\,/,$MR->trim($2);
	my $dl_select_third_part = $MR->trim($3);
	my $str = '';
	my $index = 0;
	foreach my $dl_col (@delete_columns)
	{
		if ($str ne '')
		{
            $str .= " AND \n"
        }
		$str .= $dl_col. " IN\n(". $dl_select_first_part . ' ' . $dl_select_columns[$index] . ' ' . $dl_select_third_part.')';
		
		$index += 1;
        
	}
	$cont = $delete_first_part. ' '. $str. ';';
	$cont = $CONVERTER->convert_sql_fragment($cont);
	return $cont;
}

sub finalize_content
{
	my $ar = shift;
	$MR->log_msg("finalize_content:");
	my $content = join("\n", @$ar);
	
	my $header = $Globals::ENV{CONFIG}->{header};
	my $widgets = widget_generation();
	$content = "$comment_header$header$widgets$content";
	@$ar = split(/\n/,$content);
	
	return $ar;	
}

sub fill_catalog_file
{
	my $path = shift;
	my @cont = $MR->read_file_content_as_array($path);
	foreach my $ln (@cont) #iterate through lines
	{
		my @var_cont = split(/\|/, $ln);
		$CATALOG->{uc($MR->trim($var_cont[0]))}->{uc($MR->trim($var_cont[1]))} = 1;
	}
	$MR->log_msg("Catalog File: " . Dumper($CATALOG));
}

sub get_columns_count_from_select
{
	my $content = shift;

	$content =~ s/^\s*\-\-.*$//gim;
	$content =~ s/\/\*.*?\*\///gis;
	$MR->log_msg("get_columns_count_from_select: $content");
	my $open_prent_count = 0;
	my $quotes_count = 0;
	my $column_count = 0;
	
	foreach my $char (split('', $content))
	{
		if ($char eq '*')
		{
            return -1;
        }
        
		if ($char eq '(' and $quotes_count % 2 == 0)
		{
			$open_prent_count += 1;
		}
		elsif ($char eq ')' and $quotes_count % 2 == 0)
		{
			$open_prent_count -= 1;
		}
		elsif ($char eq "'")
		{
			$quotes_count += 1;
		}
		
		if ($char eq ',' and $open_prent_count == 0 and $quotes_count % 2 == 0)
		{
			$column_count +=1;
		}
	}
	$column_count +=1;
	$MR->log_msg("get_columns_count_from_select1: $column_count");
	return $column_count;
}
