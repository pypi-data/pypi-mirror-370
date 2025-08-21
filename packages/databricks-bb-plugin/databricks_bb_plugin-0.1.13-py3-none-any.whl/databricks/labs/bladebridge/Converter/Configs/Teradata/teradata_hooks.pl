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
my $TPT = undef;
my $FastExport = undef;
my $FastLoad = undef;
my $Tpump = undef;
my $PRESCAN_MLOAD = 0;
my $PRESCAN_TPT = 0;
my $PRESCAN_FastExport = 0;
my $PRESCAN_FastLoad = 0;
my $PRESCAN_Tpump = 0;
my $FILENAME = undef;
my $export_count = 0;

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
	$PRESCAN_TPT = 0;
	$PRESCAN_FastExport =0 ;
	$PRESCAN_FastLoad = 0;
	$PRESCAN_Tpump = 0;

	foreach my $ln (@cont)
	{
		my $tmp = $ln; #don't touch the original line
		while ($tmp =~ /\$(\w+)\b(?!\.)/) #example $YEAR, $MONTH, but not $schema.table
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
		if ($ln =~ /^\s*DEFINE\s+JOB/gis)
		{
			$PRESCAN_TPT = 1;
		}
		if ($ln =~ /^\s*\.BEGIN\s+EXPORT/gis)
		{
			$PRESCAN_FastExport = 1;
		}
		if ($ln =~ /^\s*BEGIN\s+LOADING/gis)
		{
			$PRESCAN_FastLoad = 1;
		}
		if ($ln =~ /^\s*\.BEGIN\s+LOAD\b/gis)
		{
			$PRESCAN_Tpump = 1;
		}
	}

	$MR->log_msg("prescan_code_bteq completed: " . Dumper(\%PRESCAN));
	if ($PRESCAN_MLOAD)
	{
		$MR->log_msg("MLOAD BEGIN COMMAND FOUND. INVOKING MLOAD PARSER");
	}
	if ($PRESCAN_TPT)
	{
		$MR->log_msg("TPT DEFINE JOB COMMAND FOUND. INVOKING TPT PARSER");
	}
	if ($PRESCAN_FastExport)
	{
		$MR->log_msg("FastExport BEGIN COMMAND FOUND. INVOKING FastExport PARSER");
	}
	if ($PRESCAN_FastLoad)
	{
		$MR->log_msg("FastLoad BEGIN COMMAND FOUND. INVOKING FastLoad PARSER");
	}
	if ($PRESCAN_Tpump)
	{
		$MR->log_msg("Tpump BEGIN COMMAND FOUND. INVOKING Tpump PARSER");
	}

	my $ret = {PRESCAN_INFO => \%PRESCAN};
	return $ret;
}

sub init_hooks #register this function in the config file
{
	my $param = shift;
	%CFG = %{$param->{CONFIG}};
	$CFG_POINTER = $param->{CONFIG}; #give the ability to modify config incrementally
	$CONVERTER = $param->{CONVERTER};
	$MLOAD = $param->{MLOAD};
	$TPT = $param->{TPT};
	$FastExport = $param->{FastExport};
	$FastLoad = $param->{FastLoad};
	$Tpump = $param->{Tpump};
	foreach my $k (keys %$param)
	{
		$MR->log_msg("Init hooks params: $k: $param->{$k}");
	}
	$MR->log_msg("INIT_HOOKS Called. config:\n" . Dumper(\%CFG));
	$MR->log_msg("INIT_HOOKS util pointers: MLOAD: $MLOAD, TPT: $TPT, FastExport: $FastExport, FastLoad: $FastLoad, Tpump: $Tpump");

	$MLOAD->process_file($FILENAME) if $PRESCAN_MLOAD && $MLOAD;
	$TPT->process_file($FILENAME) if $PRESCAN_TPT && $TPT;
	$FastExport->process_file($FILENAME) if $PRESCAN_FastExport && $FastExport;
	$FastLoad->process_file($FILENAME) if $PRESCAN_FastLoad && $FastLoad;
	$Tpump->process_file($FILENAME) if $PRESCAN_Tpump && $Tpump;

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
	$Globals::ENV{CONFIG} = $param->{CONFIG};
	$Globals::ENV{CONFIG}->{FILENAME} = $FILENAME;
}

sub hive_finalize_code
{
	my $ar = shift;
	my $options = shift;
	my $tmp_sql = join("\n", @$ar);

	$tmp_sql = group_by_enumerations($tmp_sql);

	# Put SQL back into array
	my @cont = split("\n", $tmp_sql);
	while (scalar(@$ar) >= 1) {shift(@$ar);} #blank out the array.  Can't assign a new array, bc it is passed by ref
	foreach my $fr (@cont)
	{
		push(@$ar, $fr);
	}
}
sub group_by_enumerations
# Convert things like "GROUP BY 1, 2, 3" to "GROUP BY COLX, COLY, COLZ"
{
	my $tmp_sql = shift;
	my $regex_parens = '(.*)\(\s*((SELECT|SEL)\s+(.*?)\s+FROM\s+([^0-9].*?)GROUP BY\s+)((\d+\s*\,\s*)*\d+)\s*\)';
	$MR->debug_msg("teradata_hooks: convert_group_by_enumerations regex_parens: " . Dumper($regex_parens));
	while ($tmp_sql =~ /$regex_parens/is)
	{
		$MR->debug_msg("teradata_hooks: GROUP BY PARENS");
		my @params = $MR->get_direct_function_args($4);
		$MR->debug_msg("teradata_hooks: convert_group_by_enumerations params: " . Dumper(@params));
		my @group_by_enum = split(",", $6);
		$MR->debug_msg("teradata_hooks: convert_group_by_enumerations group_by_enum: " . Dumper(@group_by_enum));
		my $enum_idx = 0;
		foreach my $i (@group_by_enum)
		{
			@group_by_enum[$enum_idx] = $params[$i - 1];
			$enum_idx++;
		}
		my $new_group_by = join(",", @group_by_enum);
		$MR->debug_msg("teradata_hooks: convert_group_by_enumerations new_group_by: " . $new_group_by);
		$MR->debug_msg("teradata_hooks: convert_group_by_enumerations replace_value: " . "($2$new_group_by)");

		$tmp_sql =~ s/$regex_parens/$1\($2$new_group_by\)/is;
		$MR->debug_msg("teradata_hooks: convert_group_by_enumerations new_sql: " . $tmp_sql);
	}

	my $regex_outer = '(.*)((SELECT|SEL)\s+(.*?)\s+FROM\s+([^0-9].*?)GROUP BY\s+)((\d+\s*\,\s*)*\d+)';
	while ($tmp_sql =~ /$regex_outer/is)
	{
		$MR->debug_msg("teradata_hooks: GROUP BY OUTER");
		
		$MR->debug_msg("1 " . $1);
		$MR->debug_msg("2 " . $2);
		$MR->debug_msg("3 " . $3);
		$MR->debug_msg("4 " . $4);
		$MR->debug_msg("5 " . $5);
		$MR->debug_msg("6 " . $6);
		
		my @params = $MR->get_direct_function_args($4);
		$MR->debug_msg("teradata_hooks: convert_group_by_enumerations params: " . Dumper(@params));
		my @group_by_enum = split(",", $6);
		$MR->debug_msg("teradata_hooks: convert_group_by_enumerations group_by_enum: " . Dumper(@group_by_enum));
		my $enum_idx = 0;
		foreach my $i (@group_by_enum)
		{
			@group_by_enum[$enum_idx] = $params[$i - 1];
			$enum_idx++;
		}
		my $new_group_by = join(",", @group_by_enum);
		$MR->debug_msg("teradata_hooks: convert_group_by_enumerations new_group_by: " . $new_group_by);
		$MR->debug_msg("teradata_hooks: convert_group_by_enumerations replace_value: " . "($2$new_group_by)");

		$tmp_sql =~ s/$regex_outer/$1$2$new_group_by/is;
		$MR->debug_msg("teradata_hooks: convert_group_by_enumerations new_sql: " . $tmp_sql);
	}
	return $tmp_sql;
}

sub hive_load_file_snowflake
{
	my $p = $MLOAD->{MLOAD_INFO}; #just a pointer for convenience
	$MR->log_msg("__MLOAD_PLACEHOLDER__ call hive_load_file_snowflake: " . Dumper($p));
	my @sql = (); #return SQL lines
	my $external_table = $p->{WORK_TABLE} || $p->{TARGET_TABLE} || 'UNKNOWN_EXTERNAL_TABLE';
	if ($external_table =~ /\.(.*)$/ && !(exists $p->{WORK_TABLE})) {
		$external_table = $1; #get just the last token
		$external_table =~ s/\.//gs;
	}
	$MR->log_msg("External table name check 01: $external_table");
	if ($CFG{external_table_naming_pattern}) {
		my $tmp = $CFG{external_table_naming_pattern};
		$tmp =~ s/\%TABLE_NAME\%/$external_table/g;
		$external_table = $tmp;
	}

	push(@sql, "CREATE TEMPORARY EXTERNAL TABLE $external_table", '(');
	#get column definitions


	my %f = %{$p->{FIELDS}};

	# add a new hash that removes the array and adds back the column with a unique tail, which will be cut/ignored when processing
	my %f2 = ();
	foreach my $field (keys %f)
	{
		if (ref($f{$field}) eq 'ARRAY')
		{
			my $idx = 0;
			foreach my $def (@{$f{$field}})
			{
				my $new_field = $field . '__IGNORE_COLUMN_TAIL__' . $idx++;
				$f2{$new_field} = $def;
			}
		}
		else
		{
			$f2{$field} = $f{$field};
		}
	}
	%{$p->{FIELDS}} = %f2;


	if ($p->{FIELDS}) {
		my @cols = sort {$p->{FIELDS}->{$a}->{FIELD_NUMBER} <=> $p->{FIELDS}->{$b}->{FIELD_NUMBER}} keys %{$p->{FIELDS}};
		my @col_defs = ();
		foreach my $c (@cols) #iterate through column names in the order of field numbers
		{
			#my $ln = $MR->rpad("$c", 50, ' ') . $p->{FIELDS}->{$c}->{ORIG_DATATYPE};
			my $ln = "$c  $p->{FIELDS}->{$c}->{ORIG_DATATYPE}";
			push(@col_defs, $ln);
		}
		push(@sql, join(",\n", @col_defs));
	}

	# Create SELECT cols
	my @select_cols = ();
	my $delimited_blurb = '';
	foreach my $infile (keys(%{$p->{IMPORT}})) {
		my $format = $MR->trim($p->{IMPORT}->{$infile}->{FORMAT});
		if (uc($format) eq 'FASTLOAD') {
			# something
		}
		elsif ($format =~ m{VARTEXT\s+(\S+)}i) {
			$delimited_blurb = "ROW FORMAT DELIMITED\nFIELDS TERMINATED BY $1\n";
		}
		else {
			$MR->log_error("Unhandled FORMAT: \"$format\". Defaulting to FASTLOAD (fixed-width)");
		}
		my $apply = $p->{IMPORT}->{$infile}->{APPLY};
		if ($p->{LABELS}->{$apply}) {
			my $label_code = $p->{LABELS}->{$apply};
			if ($label_code =~ m{\((.*)\)}s) {
				while ($label_code =~ m{(\w+)\s*=}sg) {
					push(@select_cols, $1);
				}
			}
		}
	}
	my $select_cols = '';
	if ($delimited_blurb) {
		$select_cols = join(",\n", @select_cols);
	}
	else {
		foreach my $select_col (@select_cols) {
			$select_col = "SUBSTR($select_col, 1, $p->{FIELDS}->{$select_col}->{LENGTH})";
		}
		$select_cols = join(",\n", @select_cols);
	}

	# split $infile into filepath and filename
	my $infile = (keys(%{$p->{IMPORT}}))[0];
	my $filepath = $1 if $infile =~ /(.*)(\/|\\)(.*)/;
	my $filename = $3 if $infile =~ /(.*)(\/|\\)(.*)/;

	my $put_template_str = "";
	if ($CFG{put_template}) {
		# open file $CFG{put_template}, read file into string
		my $put_template = $CFG{put_template};
		$put_template_str = $MR->read_file_content($put_template);

		# do substitutions of %FILENAME%, %FILE_PATH% and %TABLENAME%
		$put_template_str =~ s/\%FILE_NAME\%/$filename/g;
		$put_template_str =~ s/\%FILE_PATH\%/$filepath/g;
		$put_template_str =~ s/\%TABLE_NAME\%/$p->{TARGET_TABLE}/g;
	}

	if (!$select_cols && $p->{CONVERTED_SQL})
	{
		my @converted_sql = split("\n", $p->{CONVERTED_SQL});
		my $bracket_open = 0;
		my $values_block = 0;
		my @orig_columns = ();
		my $orig_columns_counter = 0;
		my $ln_counter = 0;
		foreach my $ln (@converted_sql)
		{
			push(@select_cols, "(") if $ln_counter == 0;

			$bracket_open++ if $ln =~ /\(/;
			$bracket_open-- if $ln =~ /\)/;

			if (!$bracket_open && $ln =~ /^\s*VALUES\b/)
			{
				$values_block = 1;
				push(@select_cols, ")");
				push(@select_cols, "SELECT");

				next;
			}

			if ($bracket_open)
			{
				$ln =~ s/^\s*,//;

				# check for a column
				if ($ln =~ /^\s*\s*(\w+)/)
				{
					my $col = $1;
					push(@select_cols, "\t $col");
					push(@orig_columns, "\t $col");
				}

				# check for a column
				if ($values_block)
				{
					if ($ln =~ /\$[0-9]+/)
					{
						my $col = $orig_columns[$orig_columns_counter++];
						push(@select_cols, $col);
					}
					else
					{
						push(@select_cols, "\t $ln") unless $ln =~ /^\s*\(\s*$/;
					}
				}
			}
			$ln_counter++;
		}

		push(@select_cols, ")") if !$values_block;

		$select_cols = join(",\n", @select_cols);

		$select_cols =~ s/select\s*,/SELECT/gi;
		$select_cols =~ s/cast\s*,//gi;
		$select_cols =~ s/\)\s*,\n/\)\n/gi;
		$select_cols =~ s/\(\s*,\n/\(\n/gi;
	}

	push(@sql, ")
$delimited_blurb
$put_template_str
COPY INTO $external_table
	FROM \@my_stage
	PATTERN='.*contacts[1-5].csv.gz'
	FILE_FORMAT=(TYPE=CSV FIELD_DELIMITER='*' SKIP_HEADER=0)
	ON_ERROR='skip_file';\n
INSERT INTO $p->{TARGET_TABLE} \n$select_cols\n FROM $external_table
");


	my $str = join("\n", @sql);

	my $expr = $CONVERTER->convert_sql_fragment($str);
	return $expr;
}

sub hive_load_file
{
	my $p = $MLOAD->{MLOAD_INFO}; #just a pointer for convenience
	$MR->log_msg("__MLOAD_PLACEHOLDER__ call hive_load_file: " . Dumper($p));
	my @sql = (); #return SQL lines
	my $external_table = $p->{TARGET_TABLE} || 'UNKNOWN_EXTERNAL_TABLE';
	if ($external_table =~ /\.(.*)$/)
	{
		$external_table = $1; #get just the last token
		$external_table =~ s/\.//gs;
	}
	$MR->log_msg("External table name check 01: $external_table");
	if ($CFG{external_table_naming_pattern})
	{
		my $tmp = $CFG{external_table_naming_pattern};
		$tmp =~ s/\%TABLE_NAME\%/$external_table/g;
		$external_table = $tmp;
	}

	push(@sql, "CREATE TEMPORARY EXTERNAL TABLE $external_table", '(');
	#get column definitions
	if ($p->{FIELDS})
	{
		my @cols = sort { $p->{FIELDS}->{$a}->{FIELD_NUMBER} <=> $p->{FIELDS}->{$b}->{FIELD_NUMBER} } keys %{$p->{FIELDS}};
		my @col_defs = ();
		foreach my $c (@cols) #iterate through column names in the order of field numbers
		{
			#my $ln = $MR->rpad("$c", 50, ' ') . $p->{FIELDS}->{$c}->{ORIG_DATATYPE};
			my $ln = "$c  $p->{FIELDS}->{$c}->{ORIG_DATATYPE}";
			push(@col_defs, $ln);
		}
		push(@sql, join(",\n", @col_defs));
	}

	# Create SELECT cols
	my @select_cols = ();
	my $delimited_blurb = '';
	foreach my $infile (keys(%{$p->{IMPORT}})) {
		my $format = $MR->trim($p->{IMPORT}->{$infile}->{FORMAT});
		if (uc($format) eq 'FASTLOAD') {
			# something
		} elsif ($format =~ m{VARTEXT\s+(\S+)}i) {
			$delimited_blurb = "ROW FORMAT DELIMITED\nFIELDS TERMINATED BY $1\n";
		} else {
			$MR->log_error("Unhandled FORMAT: \"$format\". Defaulting to FASTLOAD (fixed-width)");
		}
		my $apply = $p->{IMPORT}->{$infile}->{APPLY};
		if ($p->{LABELS}->{$apply}) {
			my $label_code = $p->{LABELS}->{$apply};
			if ($label_code =~ m{\((.*)\)}s) {
				while ($label_code =~ m{(\w+)\s*=}sg) {
					push(@select_cols, $1);
				}
			}
		}
	}
	my $select_cols = '';
	if ($delimited_blurb) {
		$select_cols = join(",\n", @select_cols);
	} else {
		foreach my $select_col (@select_cols) {
			$select_col = "SUBSTR($select_col, 1, $p->{FIELDS}->{$select_col}->{LENGTH})";
		}
		$select_cols = join(",\n", @select_cols);
	}
	push(@sql, ")
$delimited_blurb
STORED AS TEXTFILE
LOCATION '$CFG_POINTER->{external_file_prefix}$p->{TARGET_TABLE}';
\n
INSERT INTO $p->{TARGET_TABLE} (
    SELECT \n$select_cols\n FROM $external_table
);
");

	my $str = join("\n", @sql);
	my $expr = $CONVERTER->convert_sql_fragment($str);
	return $expr;
}

sub fastload_to_hive_handler {
	my $p = $FastLoad->{FastLoad_INFO};
	$MR->log_msg("__FastLoad_PLACEHOLDER__ call fastload_to_hive_handler: " . Dumper($p));
	my @sql = (); #return SQL lines
	my $external_table = $p->{TARGET_TABLE} || 'UNKNOWN_EXTERNAL_TABLE';
	if ($external_table =~ /\.(.*)$/)
	{
		$external_table = $1; #get just the last token
		$external_table =~ s/\.//gs;
	}
	$MR->log_msg("External table name check 01: $external_table");
	if ($CFG{external_table_naming_pattern})
	{
		my $tmp = $CFG{external_table_naming_pattern};
		$tmp =~ s/\%TABLE_NAME\%/$external_table/g;
		$external_table = $tmp;
	}

	push(@sql, "CREATE TEMPORARY EXTERNAL TABLE $external_table", '(');
	push(@sql, "\n$p->{DEFINE}\n");

	push(@sql, ")
ROW FORMAT DELIMITED
FIELDS TERMINATED BY $p->{DELIM}
STORED AS TEXTFILE
LOCATION '$CFG_POINTER->{external_file_prefix}$p->{FILE}';
\n
$p->{INSERT}
)
SELECT * FROM $external_table
;
");

	my $str = join("\n", @sql);
	my $expr = $CONVERTER->convert_sql_fragment($str);
	return $expr;

}

sub tpump_to_hive_handler {
	my $p = $Tpump->{Tpump_INFO};
	$MR->log_msg("__Tpump_PLACEHOLDER__ call tpump_to_hive_handler: " . Dumper($p));

	my @sql = ();                  # Return SQL lines
	my $external_table = $p->{TARGET_TABLE} || 'UNKNOWN_EXTERNAL_TABLE';
	if ($external_table =~ /\.(.*)$/) {
		$external_table = $1;         # Get just the last token
		$external_table =~ s/\.//gs;
	}
	$MR->log_msg("External table name check 01: $external_table");
	if ($CFG{external_table_naming_pattern}) {
		my $tmp = $CFG{external_table_naming_pattern};
		$tmp =~ s/\%TABLE_NAME\%/$external_table/g;
		$external_table = $tmp;
	}

	push(@sql, "CREATE TEMPORARY EXTERNAL TABLE $external_table", '(');

	# Get column definitions
	if ($p->{FIELDS}) {
		my @cols = sort { $p->{FIELDS}->{$a}->{FIELD_NUMBER} <=> $p->{FIELDS}->{$b}->{FIELD_NUMBER} } keys %{$p->{FIELDS}};
		my @col_defs = ();
		foreach my $c (@cols) {      # Iterate through column names in the order of field numbers
			my $ln = "$c  $p->{FIELDS}->{$c}->{ORIG_DATATYPE}";
			push(@col_defs, $ln);
		}
		push(@sql, join(",\n", @col_defs));
	}

	push(@sql, ")
ROW FORMAT DELIMITED
FIELDS TERMINATED BY ','
STORED AS TEXTFILE
LOCATION '$CFG_POINTER->{external_file_prefix}$p->{TARGET_TABLE}';
\n
INSERT INTO $p->{TARGET_TABLE} 
    SELECT * FROM $external_table
;
");

	my $str = join("\n", @sql);
	my $expr = $CONVERTER->convert_sql_fragment($str);
	return $expr;
}

sub teradata_preprocess
{
	my $cont = shift;
	$cont = preprocess_bteq_export($cont);
	$cont = preprocess_bteq($cont);

	$cont = preprocess_separate_here_doc($cont);
	
	$MR->log_msg("teradata_preprocess TPT flag: $PRESCAN_TPT");
	$MR->log_msg("teradata_preprocess FastExport flag: $PRESCAN_FastExport");
	$MR->log_msg("teradata_preprocess FastLoad flag: $PRESCAN_FastLoad");
	$MR->log_msg("teradata_preprocess Tpump flag: $PRESCAN_Tpump");
	return qw(__TPT_PLACEHOLDER__) if $PRESCAN_TPT;
	return qw(__FastExport_PLACEHOLDER__) if $PRESCAN_FastExport;
	return qw(__FastLoad_PLACEHOLDER__) if $PRESCAN_FastLoad;
	return qw(__Tpump_PLACEHOLDER__) if $PRESCAN_Tpump;
	return @$cont;
	#my $cont_str = join("\n",@$cont);

}

sub convert_comment {
	my $cont = shift;
	$cont =~ s{/\*}{}mg;
	$cont =~ s{\*/}{}mg;
	$cont =~ s{^}{\-\-}mg;
	return $cont;
}

sub preprocess_bteq_export {
# Remove "dot" lines (lines beginning with ".") between ".export" and ".export reset" lines
	my $cont = shift;
	my $in_export = 0;
	$export_count = 0;
	my @new_cont = ();
	foreach my $cont_line (@$cont) {
		if ($in_export && $cont_line =~ m{^\s*\.export\s+reset}i) {
			$MR->log_msg("preprocess_bteq_export: Found .export reset line: $cont_line");
			$in_export = 0;
			next;
		}
		if ($cont_line =~ m{^\s*\.export\b}i) {
			$in_export = 1;
			push(@new_cont, $cont_line);
			$MR->log_msg("preprocess_bteq_export: Found .export line: $cont_line");
			next;
		}
		if ($in_export) {
			push(@new_cont, $cont_line) unless $cont_line =~ m{^\s*\.};
		} else {
			push(@new_cont, $cont_line);
		}
	}
	return \@new_cont;
}

sub preprocess_bteq
{
	my $cont = shift; 
	my @new_cont = ();

	if($CFG{suppress_lines_starting_with})
	{

		my @ar = @{$CFG{suppress_lines_starting_with}};

		my $b = $CFG{line_suppression_behavior} || 'COMMENT';
		my $comment_start = $CFG{comment_line_start} || '--';

		foreach my $ln (@$cont)
		{
			#$self->log_msg("TEST SUPPRESS: $ln");
			foreach my $el (@ar)
			{
				if ($ln =~ /^(\s*)$el/i)
				{
				
					$ln = "$ln\;";
				
				}
			}
			push(@new_cont,$ln);
	 	}

	}
	return \@new_cont;
}

sub preprocess_separate_here_doc {
# Put the wrapper (non-here doc) parts into a separate file
	my $cont = shift;
	my @wrapper_file_content = ();
	my @here_doc_content = ();
	my $in_here_doc = 0;
	my $here_doc_end_tag = '';
	my $here_doc_outfile = '';
	my $infile_name = $Globals::ENV{CONFIG}->{FILENAME};
	my $infile_basename = $MR->get_basename($infile_name);
	my $wrapper_file_name = "$Globals::ENV{CONFIG}->{shell_script_folder}/$infile_basename";
	$wrapper_file_name =~ s{(.*)\.(.*)}{$1};
	my $ext = $2;
	# my $base_here_doc_file_name = $wrapper_file_name;
	my $base_here_doc_file_name = $MR->get_basename($wrapper_file_name);
	my $here_doc_file_name = '';
	my $here_doc_abs_name = '';
	my $here_doc_count = 1;
	$wrapper_file_name .= "_wrapper.$ext";
	foreach my $cont_line (@$cont) {
		if ($cont_line =~ m{^\s*bteq\s*(.*?)<<(?:\-)?\s*(\S+)}i) {
			($here_doc_outfile, $here_doc_end_tag) = ($1, $2);
			$in_here_doc = 1;
			$here_doc_file_name = $base_here_doc_file_name . "_hd" . $here_doc_count++ . ".hql";
			my $beeline_exec = $Globals::ENV{CONFIG}->{beeline_execution_template};
			$here_doc_abs_name = "$Globals::ENV{CONFIG}->{here_doc_folder}/" . $here_doc_file_name;
			$beeline_exec =~ s{%ABS_SCRIPTNAME%}{$here_doc_abs_name}gs;
			$beeline_exec =~ s{%BASE_SCRIPTNAME%}{$here_doc_file_name}gs;
			# push(@wrapper_file_content, "hive -f $here_doc_file_name $here_doc_outfile");
			push(@wrapper_file_content, $beeline_exec);
			$MR->log_msg("preprocess_separate_here_doc: Found BTEQ here doc begin line: $cont_line");
			push(@here_doc_content, "-- BEGIN HERE DOC: $here_doc_abs_name\n");
			next;
		}
		if ($in_here_doc && $cont_line =~ m{^\Q$here_doc_end_tag\E}i) {
			$in_here_doc = 0;
			$MR->log_msg("preprocess_separate_here_doc: Found BTEQ here doc end line: $cont_line");
			push(@here_doc_content, "-- END HERE DOC: $here_doc_abs_name\n");
			next;
		}

		if ($in_here_doc) {
			push(@here_doc_content, $cont_line);
		} else {
			push(@wrapper_file_content, $cont_line);
		}
	}

	# Check if we hit end of content in here doc, but no here doc terminator found
	if ($in_here_doc) 
	{
		$in_here_doc = 0;
		$MR->log_msg("preprocess_separate_here_doc: Hit end of file; terminating here doc");
		push(@here_doc_content, "-- END HERE DOC: $here_doc_abs_name\n");
	}

	# Write wrapper file content to file
	if (@here_doc_content) {
		$MR->write_file($wrapper_file_name, join("\n", @wrapper_file_content));
		$MR->log_msg("preprocess_separate_here_doc: Created wrapper file $wrapper_file_name");
		$Globals::ENV{CONFIG}->{WRAPPER_FILE_NAME} = $wrapper_file_name;

		# Return the here doc content only
		return \@here_doc_content;
	} else {
		$Globals::ENV{CONFIG}->{WRAPPER_FILE_NAME} = '';
		# Return without changing anything
		return $cont;
	}
}

sub convert_date_to_cast {
	my $code = shift;
	$code =~ s{
		(
			\(                      # Opening paren (or whatever char you like)
			(?: [^()]* | (?0) )*    # Match a series of non-parens or another "self"
			\)                      # Closing char
		)
	}
	{actual_convert_date_to_cast($1)}exsig;
	return $code;
}

sub actual_convert_date_to_cast {
	my $code = shift;
	$code =~ s{\((.*?)\(\s*date\s*\).*}
	          {CAST($1 AS DATE)}sig;
	return $code;
}

sub tpt_to_hive_handler {
	my $p = $TPT->{TPT_INFO}; #just a pointer for convenience
	$MR->log_msg("__TPT_PLACEHOLDER__ call tpt_to_hive_handler: " . Dumper($p));

	my $expr = 'TPT_CONVERTED_CODE';
	my $oper = 'UNDEFINED';
	my $template_name = '';
	#determine operation type: export or import
	if (!$p->{STEPS}) {
		my $err = "tpt_to_hive_handler: STEPS structure is not present!";
		$MR->log_error($err);
		return $err;
	}

	my $all_exprs = '';
	
	# Iterate over each step (each "APPLY")
	foreach my $step ( @{ $p->{STEPS} }) {

		# my $step = $p->{STEPS}->[0];
		my $apply_sql = $step->{APPLY_SQL};
		my $to_oper = $p->{OPER}->{$step->{TO_OPER}};
		my $from_oper = $p->{OPER}->{$step->{FROM_OPER}};
		my $err = '';
		$err = 'TPT TO_OPER not defined!' unless $to_oper;

		# Commented out--FROM OPERATOR is not mandatory
		# $err = 'TPT FROM_OPER not defined!' unless $from_oper;

		if ($err) {
			$MR->log_error($err);
			return $err;
		}

		if ($from_oper->{TYPE} =~ /EXPORT/gis) {
			$oper = 'EXPORT';
			$template_name = 'data_export_template';
			$expr = $CFG{$template_name};
			my $select = $from_oper->{SELECTSTMT};
			$select =~ s/^'//gis;
			$select =~ s/'$//gis;
			$select =~ s/;$//gis;
			my %subst = (
				'%PATH%' => $to_oper->{FILENAME},
				'%DELIMITER%' => $to_oper->{DELIMITER} || $CFG{default_file_delimiter},
				'%SELECT%' => $select
			);
			$expr = $MR->replace_all($expr, \%subst);

		} elsif ($from_oper->{TYPE} =~ /DATACONNECTOR PRODUCER/gis) {  # Reading data from an external device/file

			# Use fastload_to_hive_handler to produce output
			$FastLoad->{FastLoad_INFO}->{DEFINE} = $p->{SCHEMAS}->{$from_oper->{SCHEMA}};
			$FastLoad->{FastLoad_INFO}->{FILE} = $from_oper->{FILENAME};
			($FastLoad->{FastLoad_INFO}->{TARGET_TABLE}) = $apply_sql =~ m{\bINSERT\s+INTO\s+([\w.]+)}si;
			$FastLoad->{FastLoad_INFO}->{INSERT} = $apply_sql;
			$FastLoad->{FastLoad_INFO}->{DELIM} = $from_oper->{TEXTDELIMITERHEX} || $from_oper->{TEXTDELIMITER} || ',';

			# Convert TextDelimiterHex to octal, if present, otherwise check TextDelimiter
			if ($from_oper->{TEXTDELIMITERHEX}) {
				my $delim = $from_oper->{TEXTDELIMITERHEX};
				$delim =~ s{['"]}{}g;
				$FastLoad->{FastLoad_INFO}->{DELIM} = "'\\" . sprintf("%03o", oct("x$delim")) . "'";
			} elsif ($from_oper->{TEXTDELIMITER}) {
				$FastLoad->{FastLoad_INFO}->{DELIM} = $from_oper->{TEXTDELIMITER};
			} else {
				$FastLoad->{FastLoad_INFO}->{DELIM} = "'" . ',' . "'";
			}
			$expr = fastload_to_hive_handler();

		} elsif ($from_oper->{TYPE} =~ /LOAD/gis) {

		} elsif ($to_oper->{TYPE} =~ /DDL/gis) {
			$expr = $apply_sql;
			
		} else {
			$err = 'Unsupported TPT configuration.  See the log!';
			$MR->log_error($err);
			return $err;
		}

		my $quote_escape = $TPT->{TPT_INFO}->{QUOTE_ESCAPE};
		$expr =~ s{$quote_escape}{'}g;

		$expr = $CONVERTER->convert_sql_fragment($expr);

		$all_exprs .= "$expr\n";
	}
	return $all_exprs;	
}

sub fastexport_to_hive_handler {
	my $p = $FastExport->{FastExport_INFO}; #just a pointer for convenience
	$MR->log_msg("__FastExport_PLACEHOLDER__ call fastexport_to_hive_handler: " . Dumper($p));

	my $expr = 'FastExport_CONVERTED_CODE';
	my $template_name = 'data_export_template';
	$expr = $CFG{$template_name};

	my $select = $p->{SELECT};
	$select =~ s/;\s*$//gis;

	my %subst = (
		'%PATH%' => $p->{OUTFILE},
		'%DELIMITER%' => $p->{DELIMITER} || $CFG{default_file_delimiter},
		'%SELECT%' => $p->{SELECT}
	);
	$expr = $MR->replace_all($expr, \%subst);

	$expr = $CONVERTER->convert_sql_fragment($expr);
	$expr =~ s{;+}{;}g;

	return $expr;	
}

sub convert_bteq_export {
	my $input = shift;
	# $input =~ m{^\s*\.EXPORT\s+(?:reportwide|DATA)\s+FILE\s*=\s*(\S+)(.*?)}is;
	$input =~ m{^\s*\.EXPORT\s+(?:reportwide|DATA)\s+FILE\s*=\s*(\S+)(.*)}is;
	my ($filename, $sql) = ($1, $2);
	if ( ! $filename) {
		$MR->log_error("No file name found in conversion of BTEQ \".EXPORT\" statement:\n$input");
		return $input;
	}
	$MR->log_msg("convert_bteq_export - Converting this .export:\n$input\n");
	$sql .= ";";
 #  my $output = "!rm -f $filename ;\n"
 #               . "INSERT OVERWRITE LOCAL DIRECTORY '$filename'\n"
 #               . "ROW FORMAT DELIMITED FIELDS TERMINATED BY ','\n"
 #               . "$sql\n"
 #               . "!mkdir -p /tmp/$filename ;\n"
 #               . "!mv $filename/000000_0 /tmp/$filename/. ;\n"
 #               . "!rm -rf $filename ;\n"
 #               . "!mv /tmp/$filename/000000_0 $filename ;\n";

######################################
# Instead of above, we need to do this:
	$export_count++;
	my $base_file_name = $MR->get_basename($Globals::ENV{CONFIG}->{FILENAME});
	my $pre_export_file_name  = "$Globals::ENV{CONFIG}->{shell_script_folder}/" . $base_file_name . '_' . 'pre_export'  . '_' . $export_count . '.sh';
	my $post_export_file_name = "$Globals::ENV{CONFIG}->{shell_script_folder}/" . $base_file_name . '_' . 'post_export' . '_' . $export_count . '.sh';
	my $pre_export_file_content  = "rm -f $filename\n"
	                             . "dir=`dirname $filename`\n"
	                             . "rm -f \$dir/000000*\n";
	my $post_export_file_content = "dir=`dirname $filename`\n"
	                             . "cat \$dir/000000* > $filename\n"
                                 . "rm -f \$dir/000000*\n";

    $MR->write_file($pre_export_file_name,  $pre_export_file_content);
    $MR->write_file($post_export_file_name, $post_export_file_content);

    my $output = "!$pre_export_file_name ;\n"
               . "INSERT OVERWRITE LOCAL DIRECTORY '$filename'\n"
               . "ROW FORMAT DELIMITED FIELDS TERMINATED BY ','\n"
               . "$sql\n"
               . "!$post_export_file_name ;\n";
	return $output;
}

sub post_conversion_adjustment {
	my $everything = shift;
	my $cont = $everything->{CONTENT};

	# --- BEGIN: Commented out--not adjusting yet
	# Get $cont into a string for global substitutions
	# my $cont_string = join("\n", @$cont);

	# $cont_string =~ s{\b(DELETE\s+FROM\s*)(\S+)(\s+WHERE\s+)(.*?);}{adjust_delete_where($1,$2,$3,$4)}gsie;

	# $cont_string =~ s{\bUPDATE\s+
	# 	            (.*?)              # $1 = UPDATE table name and possible alias name
	# 	          \s+SET\s+
	# 	            (.*?)              # $2 = SET expression(s)
	# 	          \s+FROM\s+
	# 	            (.*?)              # $3 = FROM table name and possible alias name
	# 	          \s+WHERE\s+
	# 	            (.*?)              # $4 = WHERE clause
	# 	            (?=($|\bUPDATE\s|;))  # Next match or end
	# 	       }
	# 	       {adjust_update($1, $2, $3, $4)}gsiex;

 #    # Put $cont_string back into array
 #    @$cont = split(/\n/, $cont_string);
	# --- END: Commented out--not adjusting yet

	# Shplit out any here doc content into separate files
	my @here_doc_content = ();
	my @not_here_doc_content = ();
	my $in_here_doc = 0;
	foreach my $line (@$cont) {
		if ($line =~ m{^-- END HERE DOC: (.*)}) {
			$MR->write_file($1, join("\n", @here_doc_content));
			$in_here_doc = 0;
			next;
		}
		if ($line =~ m{^-- BEGIN HERE DOC: (.*)}) {
			$in_here_doc = 1;
			@here_doc_content = ();
			next;
		}
		if ($in_here_doc) {
			push(@here_doc_content, $line);
		} else {
			push(@not_here_doc_content, $line);
		}
	}

	# Put the wrapper file content back and return it
	if ($Globals::ENV{CONFIG}->{WRAPPER_FILE_NAME}) {
		my @wrapper_cont = $MR->read_file_content_as_array($Globals::ENV{CONFIG}->{WRAPPER_FILE_NAME});
		unlink($Globals::ENV{CONFIG}->{WRAPPER_FILE_NAME});
		$Globals::ENV{CONFIG}->{WRAPPER_FILE_NAME} = '';
		return \@wrapper_cont;
	}
	return \@not_here_doc_content;
}

sub adjust_update {
	my ($update, $set, $from, $where) = ($1, $2, $3, $4);
	my ($upd_tbl_name)   = $update =~ m{(\S+)};
	my ($upd_tbl_alias)  = "$update updtbl" =~ m{\s(\S+)};  # Get alias or default to "updtbl"
	my ($from_tbl_name)  = $from =~ m{(\S+)};
	my ($from_tbl_alias) = "$from fromtbl" =~ m{\s(\S+)};  # Get alias or default to "fromtbl"

	my $return_sql = '';

	# Split SET stmnts into column name and value (anything after "="), then save
	my @set = ();   # For storing SQL SET statements
	while ($set =~ m{(.*)\s*=\s*(.*)}g) {
		my ($set_colname, $set_colval) = ($1, $2);
		$set_colval =~ s{\s*,}{};
		my $set_expr = {};
		$set_expr->{$MR->trim($set_colname)} = $MR->trim($set_colval);
		push @set, $set_expr;
	}

	# Convert WHERE... into WHEN...
	my $when = '';
	while ($where =~ m{(.*)\s*
			(
		    	(NOT\s*)?
		    	(=|>|<|>=|<=|<>|!=|BETWEEN|LIKE|IN)
			)
			+\s*(.*)}igx) {
		my ($where_col, $where_comparator, $where_val) = ($MR->trim($1), $MR->trim($2), $MR->trim($5));
		$where_val = "TRIM($where_val)" unless ($where_val =~ m{^'|"});
		my $where_op = '';
		if ($where_col =~ m{^\s*
			(
				(AND|OR)
				(\s+NOT)?
			)\b
			(.*)}ix) {
			($where_op, $where_col) = ($MR->trim($1), $MR->trim($4));
		}
		$when .= "   $where_op TRIM($where_col) $where_comparator $where_val\n";
	}

	# Create converted SQL for return
	# $return_sql .= "\nINSERT OVERWRITE TABLE $upd_tbl_name\nSELECT\n";
	if ($ENV->{CONFIG}->{insert_statement}) {
		$return_sql .= "\n" . $ENV->{CONFIG}->{insert_statement};
		$return_sql =~ s{%TABLE_NAME%}{$upd_tbl_name\nSELECT\n};
	} else {
		$return_sql .= "\nINSERT INTO $upd_tbl_name\nSELECT\n";
	}

    foreach my $set (@set) {
    	my ($case_then, $case_else) = (values($set), keys($set));
    	$case_then = "$from_tbl_alias\.$case_then" unless($case_then =~ m{\w\.\w} || $case_then =~ m{^\s*['"]});
    	$case_else = "$upd_tbl_alias\.$case_else"  unless($case_else =~ m{\w\.\w} || $case_else =~ m{^\s*['"]});
    	my $case_as = $case_else;
    	$case_as =~ s{.*?\w\.}{};  # Remove alias from "AS"
    	$return_sql .= "CASE\nWHEN\n$when"
    	            .  "THEN\n"
    	            .  "   $case_then"
    	            .  "\nELSE\n"
    	            .  "   $case_else"
    	            .  "\nEND AS "
    	            .  "$case_as\n";
    }

    $return_sql .= "-- ==ADDITIONAL_INSERT_COLUMNS==\n"     # Placeholder for user-supplied SQL
    	        . "FROM\n"
    	        . "   $upd_tbl_name AS $upd_tbl_alias\n"
    	        . "LEFT OUTER JOIN\n"
    	        . "   $from_tbl_name AS $from_tbl_alias\n"
    	        . "ON\n"
    	        . "$when;\n";
	return $return_sql;
}

sub adjust_delete_where {
	my ($del, $del_from_tbl, $where, $where_clause) = @_;
	if ($where_clause =~ m{(\S+)\s+IN\s*\(\s*SELECT\s+(\S+)\s+FROM\s+(\S+)\s*\)}si) {
		my ($where_col, $select_col, $select_from_tbl) = ($1, $2, $3);

		my $return = "INSERT OVERWRITE TABLE $del_from_tbl\n"
		           . "    SELECT\n"
		           . "       Q1.*\n"
		           . "   FROM\n"
		           . "      $del_from_tbl AS Q1\n"
		           . "   LEFT OUTER JOIN\n"
		           . "   (\n"
		           . "   SELECT\n"
		           . "      DISTINCT $where_col\n"
		           . "   FROM\n"
		           . "      $select_from_tbl\n"
		           . "   ) AS Q2\n"
		           . "   ON\n"
		           . "       COALESCE( Q1.$where_col ,1) = COALESCE( Q2.$where_col ,1)\n"
		           . "   WHERE\n"
		           . "      Q2.$where_col IS NULL ;\n";
		return $return;
	} else {
		return ($del . $del_from_tbl . $where . $where_clause .";");
	} 
}
