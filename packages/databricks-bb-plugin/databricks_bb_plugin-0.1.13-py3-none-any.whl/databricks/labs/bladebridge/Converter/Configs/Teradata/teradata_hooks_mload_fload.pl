use strict;
use Globals;
use Data::Dumper;
use Common::MiscRoutines;
use DWSLanguage;
use File::Basename;


my $MR = new Common::MiscRoutines;
# my $LAN = new DWSLanguage();
my %CFG = (); #entries to be initialized
my $CFG_POINTER = undef;
my $CONVERTER = undef;
my %PRESCAN = ();
my $PROCEDURE_NAME = 'UNKNOWN_PROC';
my $FILENAME = undef;
my $PRESCAN_MLOAD = 1;  # hard coded for now
my $MLOAD = undef;
my $T_TO_W_ASSOCIATION = undef;
my $DML_TO_INSERT_UPDATE_ASSOCIATION = undef;
my @CONT = ();
my $SQL_PARSER = undef;
my $IS_FLOAD = undef;


sub prescan_code_mload
{
	my $filename = shift;
	$FILENAME = $filename; #save in a global var
	print "******** prescan_code_mload $filename *********\n";
	return ();
}

sub init_hooks #register this function in the config file
{
	my $param = shift;
	%CFG = %{$param->{CONFIG}};
	$CFG_POINTER = $param->{CONFIG}; #give the ability to modify config incrementally
	$CONVERTER = $param->{CONVERTER};
	$SQL_PARSER = new DBCatalog::SQLParser(CONFIG => $param->{CONFIG}, DEBUG_FLAG => 1, CONTINUE_ON_ERROR => 1);
	$IS_FLOAD = 0;

	$MLOAD = $param->{MLOAD};
	foreach my $k (keys %$param)
	{
		$MR->log_msg("Init hooks params: $k: $param->{$k}");
	}
	$MR->log_msg("INIT_HOOKS Called. config:\n" . Dumper(\%CFG));
	# $MR->log_msg("INIT_HOOKS util pointers: MLOAD: $MLOAD, TPT: $TPT, FastExport: $FastExport, FastLoad: $FastLoad, Tpump: $Tpump");

	#Reinitilize vars for when -d option is used:
	%PRESCAN = ();
	$Globals::ENV{CONFIG} = $param->{CONFIG};
	$Globals::ENV{CONFIG}->{FILENAME} = $FILENAME;
	$PROCEDURE_NAME = $MR->get_basename($FILENAME);
	$PROCEDURE_NAME =~ s/\..*$//; #get rid of file extension

	$MLOAD->process_file($FILENAME) if $PRESCAN_MLOAD && $MLOAD;

	@CONT = $MR->read_file_content_as_array($FILENAME);

	# find out if FLOAD script
	foreach my $line (@CONT)
	{
		$IS_FLOAD = 1 if $line =~ /^\s*BEGIN\s+LOADING\b/i;
		$IS_FLOAD = 1 if $line =~ /^\s*DEFINE\b/i;
	}

	# create a hash based on the 5 way relationship between the following:
	# dml -> layout/file -> target_table -> work_table

	# also capture columns for each layout instance and statements for each dml instance

	$T_TO_W_ASSOCIATION = target_to_work_table();

	# $MR->log_error(Dumper($T_TO_W_ASSOCIATION));

	get_define_table_and_file() if $IS_FLOAD;
	get_top_comments();
	get_top_comments_multiline();
	get_delete_statements();

	foreach my $dml_labels (keys %{$MLOAD->{MLOAD_INFO}->{LABELS}})
	{
		my $file_name = trim(traverse_file_for_attribute($dml_labels, 'file', 0));
		my $layout_name = trim($MLOAD->{MLOAD_INFO}->{IMPORT}->{$file_name}->{LAYOUT});
		my $target_table = trim(traverse_file_for_attribute($dml_labels, 'target_table', 1));
		my $work_table = trim((keys $T_TO_W_ASSOCIATION->{$target_table})[0]);
		my $order_of_exec = $T_TO_W_ASSOCIATION->{$target_table}->{$work_table};
		my $merge_or_insert = $DML_TO_INSERT_UPDATE_ASSOCIATION->{$dml_labels}->{MERGE_OR_INSERT};
		get_fields_for_layout($layout_name);
		get_statements_for_dml($dml_labels);

		$PRESCAN{DML_ASSOCIATIONS}->{$dml_labels}->{TGT_TABLE} = $target_table;
		$PRESCAN{DML_ASSOCIATIONS}->{$dml_labels}->{LAYOUT} = $layout_name;
		$PRESCAN{DML_ASSOCIATIONS}->{$dml_labels}->{WORK_TABLE} = $work_table;
		$PRESCAN{DML_ASSOCIATIONS}->{$dml_labels}->{FILE} = $file_name;
		$PRESCAN{DML_ASSOCIATIONS}->{$dml_labels}->{ORDER_OF_EXEC} = $order_of_exec;
		# merge is 0, insert is 1
		$PRESCAN{DML_ASSOCIATIONS}->{$dml_labels}->{MERGE_OR_INSERT_IND} = $merge_or_insert;
	}

	get_variable_declarations();

	set_values_to_ENV();
}

sub set_values_to_ENV
{
	$Globals::ENV{CONVERTER} = $CONVERTER;
	$Globals::ENV{PRESCAN} = \%PRESCAN;
	$Globals::ENV{PROCEDURE_NAME} = $PROCEDURE_NAME;
	$Globals::ENV{FILENAME} = $FILENAME;
	$Globals::ENV{PRESCAN_MLOAD} = $PRESCAN_MLOAD;
	$Globals::ENV{MLOAD} = $MLOAD;
	$Globals::ENV{T_TO_W_ASSOCIATION} = $T_TO_W_ASSOCIATION;
	$Globals::ENV{DML_TO_INSERT_UPDATE_ASSOCIATION} = $DML_TO_INSERT_UPDATE_ASSOCIATION;
	$Globals::ENV{CONT} = \@CONT;
	$Globals::ENV{SQL_PARSER} = $SQL_PARSER;
	$Globals::ENV{IS_FLOAD} = $IS_FLOAD;
	$Globals::ENV{MR} = $MR;
}

sub get_define_table_and_file
{
	my $found_define_table = 0;
	foreach my $line (@CONT)
	{
		$found_define_table = 0 if $line =~ /\;/i;
		$line =~ s/,\s*$//;

		# get file
		if ($line =~ /^\s*FILE\s*\=([\s\S]+)$/i)
		{
			my $file_name = $1;
			$file_name =~ s/\;\s*$//;
			push(@{$PRESCAN{DEFINE_TABLE_FILE}}, trim($file_name))
		}

		push(@{$PRESCAN{DEFINE_TABLE_COLUMNS}}, trim($line)) if $found_define_table && trim($line);

		push(@{$PRESCAN{DEFINE_TABLE_NAME}}, $1) if $line =~ /^\s*INSERT\s+INTO\s+(\w+\.\w+)/i;

		$found_define_table = 1 if $line =~ /^\s*DEFINE\b/i;
	}
}

sub get_variable_declarations
{
	foreach my $line (@CONT)
	{
		if ($line =~ /^\s*\w+\s*\=\s*(\"|\'|\$\w+)/)
		{
			my $in_update_or_insert = 0;
			foreach my $insert_update_block (@{$PRESCAN{INSERT_UPDATE_BLOCKS_ALL}})
			{
				$in_update_or_insert = 1 if $line =~ /^\s*\Q$insert_update_block\E\s*$/;
			}

			push(@{$PRESCAN{VARIABLE_DECLARATIONS}}, $line) if !$in_update_or_insert;
		}
	}
}

sub get_top_comments
{
	my $found_comments = 0;
	foreach my $line (@CONT)
	{
		$found_comments = 1 if ($line =~ /^\s*\#/);
		last if ($found_comments && $line =~ /^\s*\w+/);

		if ($found_comments && $line =~ /^\s*(\#|\s*)/)
		{
			push(@{$PRESCAN{TOP_COMMENTS}}, $line);
		}
	}
}

sub get_top_comments_multiline
{
	my $found_comments = 0;
	foreach my $line (@CONT)
	{
		$found_comments = 1 if ($line =~ /^\s*\/\*/);

		if ($found_comments)
		{
			push(@{$PRESCAN{TOP_COMMENTS}}, $line);
		}

		last if ($found_comments && $line =~ /^\s*[\s\S]*\*\//);
	}
}

sub get_delete_statements
{
	my $found_delete_statement = 0;
	foreach my $line (@CONT)
	{
		$found_delete_statement = 1 if ($line =~ /^\s*DELETE\s+FROM/i);

		if ($found_delete_statement)
		{
			push(@{$PRESCAN{DELETE_STATEMENTS}}, $line);
		}

		if ($found_delete_statement && $line =~ /\;/)
		{
			$found_delete_statement = 0;
			push(@{$PRESCAN{DELETE_STATEMENTS}}, "");
		}

	}
}

sub get_statements_for_dml
{
	my $dml = shift;

	my $in_dml = 0;
	my $in_insert = 0;
	my $in_update = 0;
	foreach my $line (@CONT)
	{
		if ($in_dml)
		{
			# capture the insert or update statement
			if ($line =~ /^\s*UPDATE\s+([\s\S]+)\s*$/i)
			{
				# my $table_name = $1;
				$in_update = 1;
				$in_insert = 0;
			}

			if ($line =~ /^\s*INSERT\s+INTO\s+([\s\S]+)\s*$/ || $line =~ /^\s*INSERT\s+([\s\S]+)\s*$/i)
			{
				# my $table_name = $1;
				$in_insert = 1;
				$in_update = 0;
			}

			if ($in_insert && ($line =~ /^\s*\.DML\s+LABEL\s+/ || $line =~ /^\s*\.\w+/))
			{
				$in_insert = 0;
				last; # should be last element
			}
			if ($in_update && ($line =~ /^\s*\.DML\s+LABEL\s+/ || $line =~ /^\s*\.\w+/))
			{
				$in_update = 0;
				last; # should be last element
			}

			if ($in_insert)
			{
				push(@{$PRESCAN{INSERT_UPDATE_BLOCKS}->{$dml}->{INSERT_STATEMENTS}}, $line);
				push(@{$PRESCAN{INSERT_UPDATE_BLOCKS_ALL}}, $line);
			}

			if ($in_update)
			{
				push(@{$PRESCAN{INSERT_UPDATE_BLOCKS}->{$dml}->{UPDATE_STATEMENTS}}, $line);
				push(@{$PRESCAN{INSERT_UPDATE_BLOCKS_ALL}}, $line);
			}
		}

		$in_dml = 1 if ($line =~ /^\s*\.DML\s+LABEL\s+$dml/i);
	}
}

sub get_fields_for_layout
{
	my $layout = shift;

	$MR->log_msg("get_fields_for_layout LAYOUT NAME: '$layout'");

	my $in_layout = 0;
	my $found_fields = 0;
	foreach my $line (@CONT)
	{
		if ($found_fields && !($line =~ /^\s*\.FIELD\s+([\s\S]+)\s*$/i))
		{
			$in_layout = 0;
			last;
		}

		if ($in_layout && $line =~ /^\s*\.FIELD\s+([\s\S]+)\s*$/i)
		{
			my $column_specs = $1;
			$found_fields = 1;
			push(@{$PRESCAN{LAYOUT_COLUMNS}->{$layout}}, $column_specs);
		}

		$in_layout = 1 if ($line =~ /^\s*\.LAYOUT\s+$layout/i);
	}
}

sub target_to_work_table
{
	my $in_mload = 0;
	my $in_tables = 0;
	my $in_worktables = 0;

	my @tables = ();
	my @worktables = ();
	my %table_to_worktable_association = ();

	foreach my $line (@CONT)
	{
		$in_mload = 1 if ($line =~ /\.BEGIN\s+IMPORT\s+MLOAD/i);
		$in_mload = 0 if ($line =~ /\.END\s+MLOAD/i);

		$in_tables = 1 if ($in_mload && ($line =~ /^\s*TABLES /i || $line =~ /\.BEGIN\s+IMPORT\s+MLOAD\s+TABLES /i));

		if ($in_mload && $line =~ /^\s*WORKTABLES /i)
		{
			$in_worktables = 1;
			$in_tables = 0;
		}

		$in_worktables = 0 if ($in_mload && $line =~ /^\s*ERRORTABLES /i);

		if ($in_tables)
		{
			if (($line =~ /^\s*\bTABLES\s+([\s\S]+)\s*$/i
				|| $line =~ /\.BEGIN\s+IMPORT\s+MLOAD\s+TABLES\s+([\s\S]+)\s*$/i)
				|| $line =~ /^\s*([\s\S]+)\s*$/i)
			{
				my $table = $1;
				$table =~ s/,//g;
				push(@tables, $table);
			}
		}

		if ($in_worktables)
		{
			if ($line =~ /^\s*WORKTABLES\s+([\s\S]+)\s*$/i || $line =~ /^\s*([\s\S]+)\s*$/i)
			{
				my $worktable = $1;
				$worktable =~ s/,//g;
				push(@worktables, $worktable);
			}
		}
	}

	for (my $i = 0; $i < $#tables + 1; $i++)
	{
		$table_to_worktable_association{$tables[$i]}->{$worktables[$i]} = $i + 1;
	}

	return \%table_to_worktable_association;
}

sub traverse_file_for_attribute
{
	my $attribute = shift;
	my $attribute_to_get = shift;
	my $forwards_or_backwards = shift;  # 1 = forwards, 0 = backwards

	my $ln_count = 0;
	my $in_mload = 0;

	my $regex1 = '';
	my $regex2 = '';

	if ($attribute_to_get eq 'file')
	{
		$regex1 = "^\\s*APPLY\\s+$attribute\\s*";
		$regex2 = '^\s*\.IMPORT\s+INFILE\s+([\s\S]+)\s*$';
	}

	if ($attribute_to_get eq 'target_table')
	{
		$regex1 = "^\\s*\\.DML\\s+LABEL\\s+$attribute\\s*";
		$regex2 = '^\s*(INSERT\s+INTO|UPDATE)\s+([\s\S]+)\s*$';
	}

	foreach my $line (@CONT)
	{
		$in_mload = 1 if ($line =~ /\.BEGIN\s+IMPORT\s+MLOAD/i);
		$in_mload = 0 if ($line =~ /\.END\s+MLOAD/i);

		if ($in_mload && $line =~ /$regex1/i)
		{
			$MR->log_msg("$attribute_to_get: Found $attribute on line $ln_count");

			if ($forwards_or_backwards)
			{
				for (my $i = $ln_count; $i < $#CONT + 1; $i++)
				{
					if ($CONT[$i] =~ /$regex2/i)
					{
						my $insert_update = '';
						my $out_name = '';
						if ($attribute_to_get eq 'target_table')
						{
							$insert_update = $1;
							$out_name = $2;

							$DML_TO_INSERT_UPDATE_ASSOCIATION->{$attribute}->{MERGE_OR_INSERT} = 0 if ($insert_update =~ /UPDATE/i);
							$DML_TO_INSERT_UPDATE_ASSOCIATION->{$attribute}->{MERGE_OR_INSERT} = 1 if ($insert_update =~ /INSERT/i);
						}
						else
						{
							$out_name = $1;
						}

						$MR->log_msg("$attribute_to_get: Found forwards line $i with name $out_name");
						return $out_name;
					}
				}
			}
			else
			{
				for (my $i = $ln_count; $i >= 0; $i--)
				{
					if ($CONT[$i] =~ /$regex2/)
					{
						my $out_name = $1;
						$MR->log_msg("$attribute_to_get: Found backwards line $i with file name $out_name");
						return $out_name;
					}
				}
			}

		}
		$ln_count++;
	}
}

sub trim
{
	my @out = @_;
	for (@out)
	{
		s/^[\s\n]+//g;
		# s/\n\s+/\n/g;
		s/[\s\n]+$//g;

	}
	return wantarray ? @out : $out[0];
}