use strict;
use Data::Dumper;
use Common::MiscRoutines;
use DWSLanguage;


my $MR = new Common::MiscRoutines;
my $LAN = new DWSLanguage();
my %CFG = (); #entries to be initialized
my $CFG_POINTER = undef;
my $CONVERTER = undef;

my @FRAGMENTS = ();
my @FRAGMENT_COMMENTS = ();
my @FRAGMENT_COMMENTS_SORTED = ();
my @FRAGMENT_CASE_SORTED = ();
my %PROC_VARIABLES = ();
my @PROC_VARIABLES_ARR = ();

my $df_name_number = 1;

my %STAR_SQL_KEYWORDS = (
	SELECT => 1,
	INSERT => 1,
	UPDATE => 1,
	DELETE => 1,
	MERGE => 1,
	DECLARE => 1,
	WITH => 1,
	'CREATE TABLE' => 1,
	'INNER JOIN' => 1,
	'OUTER JOIN' => 1,
	'CREATE OR' => 1,
	'ALTER TABLE' => 1,
	'DROP TABLE' => 1,
	'DROP VIEW' => 1,
	'TRUNCATE TABLE' => 1,
	'CREATE DATABASE' => 1,
	'DROP DATABASE' => 1
);

sub capture_comments
{
	my $cont = shift;
	my @part_comments = $cont =~ /(\/\*.*?\*\/|--.*?\n)/gs;
	return @part_comments;
}

sub preprocess_generic_sql
{
	my $cont = shift;

	$MR->log_msg("generic_sql_databricks_hooks_v2: Called preprocess_generic_sql");

	# reset global variables
	@FRAGMENTS = ();
	@FRAGMENT_COMMENTS = ();
	@FRAGMENT_COMMENTS_SORTED = ();
	%PROC_VARIABLES = ();
	@PROC_VARIABLES_ARR = ();
	$df_name_number = 1;

	my $cont_str = join("\n", @{$cont});
	
	$cont_str =~ s/\s+\/\s*$//g;
	my @comments = capture_comments($cont_str);

	if ($CFG{proc_variable_declaration_template})
	{
		# go through cont and capture all procedure variable declarations and add them to @PROC_VARIABLES

		my $cont_str_parsing = $cont_str;

		#remove comments for parsing
		foreach my $comment (@comments)
		{
			my $parsed_comment = $comment;
			$parsed_comment =~ s/;//gs;
			$cont_str_parsing =~ s/\Q$comment\E/$parsed_comment/s;
		}

		# capture all examples of $CFG{identify_procedure_headers}
		my @possible_proc_headers = ();

		if ($CFG{identify_procedure_headers})
		{
			foreach (@{$CFG{identify_procedure_headers}})
			{
				my $header = $_;
				my @header_matches = $cont_str_parsing =~ /$header/gis;
				push(@possible_proc_headers, @header_matches);
				last if scalar(@header_matches) > 0;
			}
		}
		my $proc_header = $possible_proc_headers[0];

		# isolate the parameters, they are in ( ) after the procedure header, and then add
		# their name to %PROC_VARIABLES => their type

		if ($proc_header)
		{
			my $params = $proc_header;
			#$params =~ s/.*\((.*)\).*/$1/gs unless $CFG{skip_procedure_parsing};
            
			my @param_list = split(/,/, $params);

			if ($#param_list != -1 || $params !~ /^\s*CREATE\b/i)
			{
				foreach my $param (@param_list)
				{
					$param =~ s/(\bAS\b|\bCREATE\b|\bOR\b|\bALTER\b|\bPROCEDURE\b|\bPROC\b|\bEDITIONABLE\b|\bREPLACE\b|\bNULL\b|\=|[\w\[\]]+\.[\w\[\]]+|[\)\(0-9\,]*)//gis;
					$param =~ s/^\s+|\s+$//g;  # trim whitespace
					$param =~ s/\bOUT\b//gis;  # remove the OUT keyword
					next unless $param;
					my @param_parts = split(/\s+/, $param);
					my $param_name = $param_parts[0];
					my $param_type = $param_parts[1];
					$PROC_VARIABLES{$param_name} = $param_type;
					push(@PROC_VARIABLES_ARR, $param_name)
				}
            }
		}
	}

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
	elsif($CFG{remove_comments})
	{
		$cont_str = remove_comments($cont_str);
	}
	else
	{
		foreach my $comment (@comments)
		{
			my $parsed_comment = $comment;
			$parsed_comment =~ s/;//gs;
			$cont_str =~ s/\Q$comment\E/$parsed_comment/s;
		}
	}

	# remove case statements and add them back (END keyword is removed to not affect splitting)
	my @case_statements = $cont_str =~ /(\bCASE\s+WHEN\b[\s\S]+?\bEND\b)/gis;
	my $comm_idx = 0;
	@FRAGMENT_CASE_SORTED = @case_statements;
	#sort by length, largest first
	@FRAGMENT_CASE_SORTED = sort { length($b) <=> length($a) } @FRAGMENT_CASE_SORTED;

	foreach my $case (@FRAGMENT_CASE_SORTED)
	{
		my $replacement = "__BB_CASE_" . $comm_idx . "__";
		$cont_str =~ s/\Q$case\E/$replacement\n/s;
		$comm_idx++;
	}

	if (exists $CFG{pre_process_subst})
	{
		$cont_str = from_to_substitution($CFG{pre_process_subst}, $cont_str);
	}

	$cont_str = process_columns($cont_str) if $CFG_POINTER->{process_square_bracket_columns};

	$cont_str =~ s/\bLOOP\s+UPDATE\b/\n;UPDATE/gi;
	$cont_str =~ s/\bEXIT\s+WHEN\b.*$//im;
	$cont_str =~ s/\<\<.*?\>\>\s*//g;
	$cont_str =~ s/\bOPEN\s+\w+\s*\;//i;
	$cont_str =~ s/\bTYPE\s+\w+\s+IS\s+RECORD\b\s*\(.*?\)\s*\;//gis;
	$cont_str =~ s/\bTYPE\s+\w+\s+IS\s+TABLE\s+OF.*?\%ROWTYPE\s*\;//i;

	$cont_str =~ s/\bwhen\s+(__BB_COMMENT_[0-9]__)*\s*others\s+(__BB_COMMENT_[0-9]__)*\s*then\b\s*//gis;
	$cont_str =~ s/\bwhen\s+(__BB_COMMENT_[0-9]__)*\s*NO_DATA_FOUND\s+(__BB_COMMENT_[0-9]__)*\s*then\b\s*//gis;

	# split fragments
	my $default_frag_regex = ';';
	$cont_str =~ s/\bTHEN\s+UPDATE\b/__THEN__UPDATE__/gis;
	$default_frag_regex = $CFG{fragment_split_regex} if $CFG{fragment_split_regex}; 
	@FRAGMENTS = split(/$default_frag_regex/i, $cont_str);
	
	foreach (@FRAGMENTS)
	{
		$_ =~ s/__THEN__UPDATE__/THEN UPDATE/gis;
	}
	
	my @fr = ();
	if ($CFG{fragment_sub_split_regex})
	{
		my $sub = $CFG{fragment_sub_split_regex};
       	foreach (@FRAGMENTS)
		{
			@fr = (@fr,split(/$sub/is, $_))
		}
		@FRAGMENTS = @fr;
    }
	
	if ($CFG{save_normal_end_statement})
	{
		# Combine fragments starting with "END AS" with the previous fragment
		for (my $i = 1; $i < @FRAGMENTS; $i++)
		{
			if ($FRAGMENTS[$i] =~ /^\s*\bEND\s+AS\b/)
			{
				$FRAGMENTS[$i] =~ s/^\s*\bEND\s+AS\b/#__NORMAL_END__ AS/is if $CFG{save_normal_end_statement};
				$FRAGMENTS[$i-1] .= $FRAGMENTS[$i];
				splice(@FRAGMENTS, $i, 1);
				$i--; # Adjust index after splice
			}
		}
	}

	my $idx = 0;
	foreach (@FRAGMENTS)
	{
		# check for single or multiline sql comments and
		# if they exist remove them from $_ and add them to @FRAGMENT_COMMENTS at the same $idx

		my @frag_comments = capture_comments($_);
		my @frag_comment_sorted = @frag_comments;
		#sort by length, largest first
		@frag_comment_sorted = sort { length($b) <=> length($a) } @frag_comment_sorted;

		if (scalar(@frag_comments) >= 1 && !$CFG{keep_comments_in_place})  # found comments
		{
			foreach my $comment (@frag_comment_sorted)
			{
				$_ =~ s/\Q$comment\E//gs;
			}

			$FRAGMENT_COMMENTS[$idx] = join("\n", @frag_comments);
		}
		else
		{
			$FRAGMENT_COMMENTS[$idx] = "";
		}

		$idx++;
	}

	# split fragments again for grouped fragments such as for loops and conditionals with inner statements
	$idx = 0;
	foreach (@FRAGMENTS)
	{
		my $frag = $_;

		my $cat_fragment = $frag;
		$cat_fragment =~ s/__BB_COMMENT_[0-9]+__//gs;

		#get category of fragment
		my $cat = $CONVERTER->categorize_statement($cat_fragment);

		# $MR->log_error("fragment: $frag, category: $cat");

		my @frag_parts = ();
		$frag_parts[0] = $frag;

		if ($cat eq "DECLARE" || $cat eq "FUNCTION_CALL")
		{
			$frag =~ s/\(\s*\bSELECT\b/__PRSL__/gis;
			@frag_parts = split(/(?=\bSELECT\b)/i, $frag);
			foreach (@frag_parts)
			{
				$_ =~ s/__PRSL__/(SELECT/gis;
			}
		}
		elsif ($cat eq "PYTHON_FOR_LOOP")
		{
			# split by LOOP or BEGIN
			@frag_parts = split(/\bLOOP\b|(\bBEGIN\b|\bEXCEPTION\b)/i, $frag);
		}
		elsif ($cat eq "PYTHON_PRINT")
		{
			# split by semicolon
			@frag_parts = split(/;/i, $frag);
		}
		elsif ($cat eq "PYTHON_CONDITIONAL")
		{
			@frag_parts = split(/(?<!\bMATCHED )(?<!\bNULL )\bTHEN\b|(\bSET\b|\bELSE\b|\bBEGIN\b|\bEXCEPTION\b)/i, $frag);

			# if a fragment starts with ^\s*[0-9] then combine it with the previous fragment
			# (part of case statement or another construct)
			my $frag_idx = 0;
			foreach my $frag_part (@frag_parts)
			{
				if ($frag_part =~ /^\s*[0-9]/)
				{
					$frag_parts[$frag_idx - 1] .= $frag_part;
					splice(@frag_parts, $frag_idx, 1);
				}
				$frag_idx++;
			}

			# if a fragment has \bcase\s+when\b and it ends with [0-9]
			# and then next fragment starts with ^\s*ELSE then combine
			# the two fragments (part of case statement)
			$frag_idx = 0;
			foreach my $frag_part (@frag_parts)
			{
				if ($frag_part =~ /\bCASE\b\s+WHEN\b/i && $frag_part =~ /\b[0-9]\s*$/)
				{
					if ($frag_parts[$frag_idx + 1] =~ /^\s*ELSE\b/i)
					{
						$frag_parts[$frag_idx] .= $frag_parts[$frag_idx + 1];
						splice(@frag_parts, $frag_idx + 1, 1);
					}
				}
				$frag_idx++;
			}
		}
		else
		{
			@frag_parts = split(/(\bBEGIN\b|\bEXCEPTION\b)/i, $frag);

			@frag_parts = split(/(\bBEGIN\b|\bEXCEPTION\b|\bTRY\b|\bCATCH\b)/i, $frag) if $CFG{try_catch_split};
		}

		# delete blank strings from @frag_parts
		@frag_parts = grep { $_ ne '' } @frag_parts;

		if (scalar(@frag_parts) > 1)
		{
			# remove $FRAGMENTS[$idx] and add @frag_parts to $FRAGMENTS in it's place
			splice(@FRAGMENTS, $idx, 1, @frag_parts);
		}

		$idx++;
	}
	# foreach fragment do a post_fragment_subst
	if (exists $CFG{post_fragment_subst})
	{
		$idx = 0;
		foreach my $frag (@FRAGMENTS)
		{
			$FRAGMENTS[$idx] = from_to_substitution($CFG{post_fragment_subst}, $frag);
			$idx++;
		}
	}


	$cont_str = "";

	@{$cont} = split(/\n/, $cont_str);
	return @{$cont};
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

sub init_hooks #register this function in the config file
{
	my $param = shift;
	%CFG = %{$param->{CONFIG}};
	$CFG_POINTER = $param->{CONFIG}; #give the ability to modify config incrementally
	$CONVERTER = $param->{CONVERTER};
	$MR = new Common::MiscRoutines unless $MR;
	#print "INIT_HOOKS Called. MR: $MR. config:\n" . Dumper(\%CFG);

	$MR->log_msg("generic_sql_databricks_hooks_v2: Called init_hooks\n" . Dumper(\%CFG));

}

sub frag_handler
{
	my $input = shift;

	my $cat_fragment = $input;
	$cat_fragment =~ s/__BB_COMMENT_[0-9]+__//gs;

	my $cat = $CONVERTER->categorize_statement($cat_fragment);

	$cat = '__DEFAULT_HANDLER__' if $cat eq '';
	$MR->log_msg("Category: $cat");
	# $MR->log_error("Input: $input, Category: $cat");

	my $handler = $CFG{fragment_handling}->{$cat};
	$MR->log_msg("handle_when_then: fragment handling handler: $handler");
	my $eval_str = $handler . '([$input]);';
	$input = eval($eval_str);

	my $return = $@;
	if ($return)
	{
		$MR->log_error("************ EVAL ERROR: $return ************");
	}
	else
	{
		$input = join("\n", @{$input});
		$MR->log_msg("handle_when_then: Then fragment converted: $input");
	}

	return $input;
}

sub finalize_content
{
	my $ar = shift;
	my $str_content = join("\n", @{$ar});

	$str_content = "";  # set blank
	my @out_frags = ();

	my $idx = 0;
	foreach my $frag (@FRAGMENTS)
	{
		my $origninal_frag = $frag;
		$frag = frag_handler($frag);

		# add back the case statements
		$idx = 0;
		foreach my $case (@FRAGMENT_CASE_SORTED)
		{
			my $replacement = "__BB_CASE_" . $idx . "__";
			$case =~ s/(\bEND\b|\bEND\s*\;)/#__NORMAL_END__/gis if $CFG{save_normal_end_statement};

			my $ar_temp = [$case];
			$ar_temp = generic_substitution($ar_temp, "default_sql_subst");
			$case = join("\n", @{$ar_temp});

			$frag =~ s/\Q$replacement\E/$case/s;
			$idx++;
		}

		if ($CFG{keep_comments_in_place})
		{
			$idx = 0;
			foreach my $comment (@FRAGMENT_COMMENTS_SORTED)
			{
				my $replacement = "__BB_COMMENT_" . $idx . "__";
				my $replacement2 = "__BB_SQL_COMMENT_" . $idx . "__";

				my $cat_fragment = $origninal_frag;
				$cat_fragment =~ s/__BB_COMMENT_[0-9]+__//gs;
				$cat_fragment =~ s/__BB_SQL_COMMENT_[0-9]+__//gs;
				my $cat = $CONVERTER->categorize_statement($cat_fragment);

				if ($CFG{comment_quote_replacement})
				{
					$comment =~ s/\"/__BG_QUOTE__/gis;
					$comment =~ s/\'/__QUOTE__/gis;
				}

				$frag =~ s/\Q$replacement2\E/ $comment /s;

				if (($cat eq '' || $cat eq 'CURSOR_DEF' || $cat eq 'PYTHON_FOR_LOOP'
					|| $cat eq 'SELECT_INTO') && !($frag =~ /^\s*\# COMMAND ----------\s*\bEND\b/si))
				{
					$frag =~ s/\Q$replacement\E/ $comment /s;
				}
				else
				{
					$frag =~ s/\Q$replacement\E/\"\"\"$comment\"\"\"/s;
				}
				$idx++;
			}
		}

		push(@out_frags, $frag) if $frag ne "";

		$FRAGMENT_COMMENTS[$idx] =~ s/\"/\\\"/g;
		push(@out_frags, "\"\"\"COMMENTS:\n\n" . $FRAGMENT_COMMENTS[$idx]. "\"\"\"") if $FRAGMENT_COMMENTS[$idx] ne "";
		$idx++;
	}

	my $in_between = $CFG{between_sql_fragments} || "\n\n";
	$str_content = join($in_between, @out_frags);

	# call convert_sql_fragment
	$str_content = $CONVERTER->convert_sql_fragment($str_content);
	$str_content = try_except_handling($str_content) if $CFG{try_except_handling};
	$str_content = add_file_tabbing($str_content) if $CFG{file_tabbing};

	# add in proc variable header
	my $proc_var_header = "";
	foreach my $var (keys %PROC_VARIABLES)
	{
		my $var_type = $PROC_VARIABLES{$var};
		next if $var_type eq "__NO_DECLARATION__";
		my $var_dec = $CFG{proc_variable_declaration_template};
		$var = $1 if $var =~ /^\s*\@(\w+)\s*$/;
		$var_dec =~ s/\%VARNAME\%/$var/g;
		my $default_val = $CFG{proc_variable_default_widget_value} || "";
		$var_dec =~ s/\%DEFAULT_VALUE\%/$default_val/g;
		$proc_var_header .= $var_dec unless $var =~ /^\s*[0-9]+\s*$/;
	}

	if ($CFG{proc_variable_declaration_header})
	{
		$str_content = $CFG{proc_variable_declaration_header} . "\n" . $proc_var_header . "\n" . $str_content;
	}

	# add post_process_header
	if ($CFG{post_process_header})
	{
		$str_content = $CFG{post_process_header} . "\n" . $str_content;
	}

	# add footer
	if ($CFG{post_process_footer})
	{
		$str_content = $str_content . "\n" . $CFG{post_process_footer};
	}

	@{$ar} = split(/\n/,$str_content);

	$ar = generic_substitution($ar, "final_visual_subst");
	$str_content = join("\n", @{$ar});

	my @insert_tables;
	while ($str_content =~ /\bINSERT\s+INTO\s+([\w\.]+)/ig)
	{
		unshift @insert_tables, $1; # Add the match to the beginning of the array
	}

	# If no matches are found, add a default value
	@insert_tables = ('__NO_INSERT_TABLE_FOUND__') if @insert_tables == 0;

	if ($CFG{insert_table_exceptions})
	{
		my @exceptions = @{$CFG{insert_table_exceptions}};
		foreach my $exception (@exceptions)
		{
			@insert_tables = grep { $_ ne $exception } @insert_tables;
		}
	}

	# make @insert_tables unique
	my %seen = ();
	@insert_tables = grep { ! $seen{$_}++ } @insert_tables;

	# create a string array of insert tables
	my $insert_tables_str = '[' . join(', ', map { "\"$_\"" } @insert_tables) . ']';
	$str_content =~ s/\%INSERT_TABLES\%/$insert_tables_str/gs;
	$str_content = add_python_def_replacement($str_content);
	$str_content = add_finalized_tabs($str_content);

	@{$ar} = split(/\n/, $str_content);

	return $ar;
}

sub add_python_def_replacement
{
	my $str_content = shift;

	my $name = $CONVERTER->{CURRENT_ITEM};
	my $def_name = $name;
	# remove file extensions
	$def_name =~ s/\.\w+$//g;
	# remove dots
	$def_name =~ s/\./_/g;

	# get params captured for widgets
	my @params = ();
	my @default_params = ();
	foreach my $var (@PROC_VARIABLES_ARR)
	{
		my $var_type = $PROC_VARIABLES{$var};
		next if $var_type eq "__NO_DECLARATION__";
		$var = $1 if $var =~ /^\s*\@(\w+)\s*$/;
		push(@params, $var);
		push(@default_params, "\"" . $CFG{proc_variable_default_widget_value} . "\"");
	}
	my $params = "";
	$params = ", " . join(", ", @params) if scalar(@params) > 0;
	my $default_params = ", " . join(", ", @default_params) if scalar(@default_params) > 0;

	my $def_str = "";
	$def_str = $CFG{python_function_signature} if $CFG{python_function_signature};
	$def_str =~ s/\%PROC_NAME\%/$def_name/g;
	my $call_def_str = $def_str;
	$def_str =~ s/\%PARAMS\%/$params/g;
	$str_content =~ s/\%DEF_CALL_SIGNATURE\%/$def_str/gs;

	$call_def_str =~ s/\%PARAMS\%/$default_params/g;
	$str_content =~ s/\%DEF_CALLED_SIGNATURE\%/$call_def_str/gs;

	$str_content =~ s/\%PROC_NAME\%/$def_name/g;

	return $str_content;
}


sub add_finalized_tabs
{
	my $str_content = shift;

	# we have markers '# end header' and '# begin footer'.
	# go line by line, after '# end header' add tabs to lines and after '# begin footer' stop adding tabs
	my $header_end = 0;
	my $footer_begin = 0;
	my $tabbing = $CFG{file_tabbing} || "\t";
	my @lines = split(/\n/, $str_content);
	foreach (@lines)
	{
		if ($_ =~ /^\s*#\s*begin\s*footer\s*$/i)
		{
			$footer_begin = 1;
		}

		if ($header_end == 1 && $footer_begin == 0)
		{
			$_ = $tabbing . $_;
		}

		if ($_ =~ /^\s*#\s*end\s*header\s*$/i)
		{
			$header_end = 1;
		}
	}
	$str_content = join("\n", @lines);

	# remove the markers
	$str_content =~ s/(\s*)\#\s*end\s*header\b/$1/gi;
	$str_content =~ s/(\s*)\#\s*begin\s*footer\b/$1/gi;

	# convert 4 spaces to tabs
	$str_content =~ s/    /\t/g;

	return $str_content;
}

sub try_except_handling
{
	my $str = shift;
	if($CFG{remove_comments})
	{
		$str = remove_comments($str);
	}
	my @lines = split(/\n/, $str);

	# for each line in the array, find all line numbers that have
	# __TRY_EXCEPT__ and store them in an array

	my @try_except_lines = ();
	my @try_except_line_numbers = ();
	my $line_number = 0;
	foreach my $line (@lines)
	{
		if ($line =~ /__TRY_EXCEPT__/)
		{
			push(@try_except_line_numbers, $line_number);
			push(@try_except_lines, $line);
		}
		$line_number++;
	}

	my @modified_try_except_lines = ();

	# for each line in @try_except_lines,
	# replace all \bBEGIN\b lines with try:
	# replace all \bEXCEPT\b lines with except:
	# replace all \bEND\b lines with except only if there was not an \bEXCEPT\b line before it

	my $except_flag = 0;
	foreach (@try_except_lines)
	{
		if ($_ =~ /\bBEGIN\b/i)
		{
			$_ = "try:";
		}
		elsif ($_ =~ /\EXCEPTION\b/i)
		{
			$_ = "except:";
			$except_flag = 1;
		}
		elsif ($_ =~ /\bEND\b/i)
		{
			if ($except_flag == 0)
			{
				$_ = "except:\npass";
			}
			else
			{
				$_ = "#__ignored_except__";
				$except_flag = 0;
			}
		}

		push(@modified_try_except_lines, $_);
	}


	# for each line number, go through the array and replace the line with the modified line
	foreach my $line_numb (@try_except_line_numbers)
	{
		$lines[$line_numb] = $modified_try_except_lines[0];
		shift(@modified_try_except_lines);
	}

	return join("\n", @lines);
}

sub add_file_tabbing
{
	my $str = shift;
	my $tabbing = $CFG{file_tabbing} || "\t";

	my $tab_counter = 0;

	my @lines = split(/\n/, $str);
	foreach (@lines)
	{
		# remove all spaces from beginning of line
		$_ =~ s/^\s+//;

		if ($_ =~ /^\s*(elif)\s+/i)
		{
			$tab_counter--;
		}

		if ($_ =~ /^\s*(else\:)\s*/i)
		{
			$tab_counter--;
		}

		if ($_ =~ /^\s*(except\:)\s*/i)
		{
			$tab_counter--;
		}

		if ($_ =~ /__TAB_ADD__/i)
		{
			$tab_counter++;
		}

		# adding tabs multiplied by tab_counter
		# $_ = $tabbing x $tab_counter . $_ . "   tab counter: $tab_counter";
		$_ = $tabbing x $tab_counter . $_;

		if ($_ =~ /__TAB_DEL__/i)
		{
			$tab_counter--;
		}

		if ($_ =~ /^\s*(try\:)\s*/i)
		{
			$tab_counter++;
		}

		if ($_ =~ /^\s*(except\:)\s*/i)
		{
			$tab_counter++;
		}

		if ($_ =~ /^\s*(pass)\s*/i)
		{
			$tab_counter--;
		}

		if ($_ =~ /^\s*(#__ignored_except__)\s*/i)
		{
			$tab_counter--;
		}

		if ($_ =~ /^\s*(elif)\s+/i)
		{
			$tab_counter++;
		}

		if ($_ =~ /^\s*(else\:)\s*/i)
		{
			$tab_counter++;
		}

		#if starts with 'for' set tab counter to 1
		if ($_ =~ /^\s*for\s+/i)
		{
			$tab_counter++;
		}

		#if starts with 'if' add to tab counter
		if ($_ =~ /^\s*(if)\s+/i)
		{
			$tab_counter++;
		}

		#if starts with '#__endif__' make tab counter 0
		if ($_ =~ /^\s*#__endif__\s*/i)
		{
			$tab_counter--;
		}

		#if starts with '#__endloop__' make tab counter 0
		if ($_ =~ /^\s*#__endloop__\s*$/i)
		{
			$tab_counter--;
		}

		if (exists $CFG{custom_tab_back_regex} && $CFG{custom_tab_back_regex})
		{
			if ($_ =~ /$CFG{custom_tab_back_regex}/i)
			{
				$tab_counter--;
			}
		}

		if (exists $CFG{custom_tab_forward_regex} && $CFG{custom_tab_forward_regex})
		{
			if ($_ =~ /$CFG{custom_tab_forward_regex}/i)
			{
				$tab_counter++;
			}
		}
	}

	my $out = join("\n", @lines);

	$out =~ s/__TAB_ADD__//g;
	$out =~ s/__TAB_DEL__//g;

	return $out;
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

sub try_except
{
	my $ar = shift;

	my $cont_str = join("\n", @{$ar});
	if($CFG{remove_comments})
	{
		$cont_str = remove_comments($cont_str);
	}
	# remove \n from start of string
	$cont_str =~ s/^[\s\n]*//;
	$cont_str = "\n#" . $cont_str . " __TRY_EXCEPT__";
	@{$ar} = split(/\n/, $cont_str);

	$ar = generic_substitution($ar, "try_except_subst");

	return $ar;
}

sub python_conditional
{
	my $ar = shift;

	# for sql statements
	my $out = generic_substitution($ar, "pre_python_conditional_subst");
	my $cont_str = join("\n", @{$out});

	# split by or, and
	my @mini_frags = split(/(?=\bor\b|\band\b)/i, $cont_str);

	my @out_mini_frags = ();
	# for each mini fragment if $mini_frag !~ /\bspark\.sql\s*\(/ then do
	foreach my $mini_frag (@mini_frags)
	{
		if ($mini_frag !~ /\bspark\.sql\s*\(/)
		{
			my $temp_ar = [$mini_frag];
			my $mini_out = generic_substitution($temp_ar, "python_conditional_subst");
			push(@out_mini_frags, join("\n", @{$mini_out}));
		}
		else
		{
			push(@out_mini_frags, $mini_frag);
		}
	}

	# join the fragments back together into $cont_str
	$cont_str = join("", @out_mini_frags);

	#trim whitespace from beginning and end of string
	$cont_str =~ s/^\s+|\s+$//g;

	# add :
	$cont_str .= ":";

	# make lowercase
	$cont_str =~ s/\bIF\b/if/s;
	$cont_str =~ s/\bAND\b/and/gs;
	$cont_str =~ s/\bOR\b/or/gs;

	@{$out} = split(/\n/, $cont_str);
	return $out;
}

sub python_for_loop
{
	my $ar = shift;
	my $out = generic_substitution($ar, "python_for_loop_subst");
	my $cont_str = join("\n", @{$out});

	my @start_comments = ();
	while ($cont_str =~ /^(\s*)(__BB_COMMENT_[0-9]+__)(.*)/s)
	{
		push(@start_comments, $1.'"""'.$2.'"""'."\n");
		$cont_str = $3;
	}

	#trim whitespace from beginning and end of string
	$cont_str =~ s/^\s+|\s+$//g;

	# add :
	$cont_str .= ":";

	# if a select statement
	if ($cont_str =~ /\(\s*(\bSELECT\b[\s\S]+)\)\s*\:\s*$/gi)
	{
		my $sql_statement = $1;
		$cont_str =~ s/\(\s*\Q$sql_statement\E\s*\)/last_query_res/gi;
		$cont_str = "last_query_val = spark.sql(f\"\"\"" . $sql_statement . "\"\"\")\nlast_query_res = last_query_val.collect()[0]\n" . $cont_str;
	}

	# if a function call
	if ($cont_str =~ /\bin\b\s*(\w+\s*\([\s\S]+)\s*:\s*$/gi)
	{
		my $func_call = $1;
		$cont_str =~ s/\Q$func_call\E/last_func_call_res/gi;
		$cont_str = "last_func_val = $func_call\nlast_func_call_res = last_func_val.collect()\n" . $cont_str;
	}

	$cont_str = join("\n", @start_comments) . $cont_str;


	@{$out} = split(/\n/, $cont_str);
	return $out;
}

sub python_variable_declaration
{
	my $ar = shift;
	my $cont_str = join("\n", @{$ar});
	return generic_substitution($ar, "python_variable_declaration_subst");
}

sub python_variable_assignment
{
	my $ar = shift;
	return generic_substitution($ar, "python_variable_assignment_subst");
}

sub generic_substitution
{
	my $ar = shift;
	my $cfg_subst = shift;

	my $cont_str = join("\n", @{$ar});
	#$cont_str =~ s/\'\'\'/\'/g;
	if($CFG{remove_comments})
	{
		$cont_str = remove_comments($cont_str);
	}
	
	if ($MR->trim($cont_str) eq "'")
	{
        $cont_str = '';
    }
    
	#block substitution for variable declarations from config
	if (exists $CFG{$cfg_subst})
	{
		$cont_str = from_to_substitution($CFG{$cfg_subst}, $cont_str);
	}

	@{$ar} = split(/\n/, $cont_str);
	return $ar;
}
sub python_loop_fetch
{
	my $ar = shift;
	my $cont_str = join("\n", @$ar);

	$cont_str =~ /\bLOOP\s+FETCH\b\s+(\w+).*?\bINTO\b\s+(\w+)/gi;
	@$ar = ("for $2 in $1:");
	return $ar;
}
sub delete_fragment
{
	my $ar = shift;

	my $cont_str = join("\n", @{$ar});
	$cont_str = "";
	@{$ar} = split(/\n/, $cont_str);
	return $ar;
}

sub set_execute
{
	my $ar = shift;

	my $cont_str = join("\n", @{$ar});


	if ($cont_str =~ /\;/)
	{
		# split by ';' -- should be 2 parts, set and execute
		my @mini_frags = split(/;/, $cont_str);
		my $set_statement = $mini_frags[0];
		my $execute_statement = $mini_frags[1];

		# fetch the variable name from the execute statement
		# example: EXECUTE SP_EXECUTESQL @V_SQL, @PARAMS = N'@V_OUT INT OUTPUT, @V_OUT_1 INT OUTPUT', @V_OUT = @V_PRCS_ID OUTPUT, @V_OUT_1 = @V_JOB_ID OUTPUT;

		# the first \@(\w+) should be saved as initial variable
		my $initial_variable = "";
		$initial_variable = $1 if $set_statement =~ /\@(\w+)/is;

		my %variable_names = ();
		while ($execute_statement =~ /\@(\w+)\s*=\s*\@(\w+)\s*OUTPUT/gi)
		{
			$variable_names{$1} = $2;
		}

		$set_statement = "$1 = spark.sql(f\'\'\'$3\'\'\').collect()" if $set_statement =~ /^\s*SET\b\s+\@(\w+)\s*\=\s*\N(\'|\"|\'\'\'|\"\"\")([\s\S]+?)\2\s*$/is;
		$set_statement = "$1 = spark.sql(f\'\'\'$3\'\'\').collect()" if $set_statement =~ /^\s*SET\b\s+\@(\w+)\s*\=\s*\N(\'|\"|\'\'\'|\"\"\")([\s\S]+?)\s*$/is;
		# $set_statement =~ s/\@(\w+)/{$1}/g;
		# $set_statement =~ s/(\'\s*\+|\+\s*\')//gs;

		my $ar_2 = [$set_statement];
		generic_substitution($ar_2, "set_execute_subst");
		$set_statement = join("\n", @{$ar_2});

		# for each key in %variable_names, replace the key with the value in $set_statement
		foreach my $key (keys %variable_names)
		{
			$set_statement =~ s/\b$key\b/$variable_names{$key}/g;
		}

		# add in try catch for variable assignment
		my @try_assignments = ();
		my @except_assignments = ();
		foreach my $key (keys %variable_names)
		{
			push(@try_assignments, "$variable_names{$key} = $initial_variable\[0\][$variable_names{$key}]");
			push(@except_assignments, "$variable_names{$key} = 0");
		}

		my $try_string = "__TR__:\n__TAB_ADD__" . join("\n", @try_assignments) . "\n__TAB_DEL__\n __EXCP__:\n__TAB_ADD__" . join("\n", @except_assignments) . "\n__TAB_DEL__";

		$cont_str = $set_statement . "\n" . $try_string;
	}


	@{$ar} = split(/\n/, $cont_str);
	return $ar;
}

sub declare_fragment
{
	my $ar = shift;
	$ar = generic_substitution($ar, "declare_subst");
	my $cont_str = join("\n", @{$ar});

	if ($cont_str =~ /(\w+)\s*\=\s*[\s\S]+?\;/i)
	{
		$PROC_VARIABLES{$1} = "__NO_DECLARATION__" unless exists $PROC_VARIABLES{$1};
	}

	@{$ar} = split(/\n/, $cont_str);
	return $ar;
}

sub sp_log
{
	my $ar = shift;
	return generic_substitution($ar, "sp_log_subst");
}

sub python_print
{
	my $ar = shift;
	return generic_substitution($ar, "python_print_subst");
}

sub set_sql
{
	my $ar = shift;
	return generic_substitution($ar, "set_sql_subst");
}

sub cursor_for_loop
{
	my $ar = shift;
	return generic_substitution($ar, "cursor_for_loop_pre_subst");
}

sub function_call
{
	my $ar = shift;
	$ar = generic_substitution($ar, "function_call_subst");
	my $cont_str = join("\n", @{$ar});

	# remove [ and ] from $cont_str
	$cont_str =~ s/\[|\]//g;

	if ($cont_str =~ /\bexec\s+(\w+\.\w+)([\s\'\w\,\@\{\}\.]+)/i)
	{
		my $stored_proc_name = $1;
		my $params = $2;

		# collect all the parameters and store names in array, split by comma
		my @param_names = split(/\,/, $params);

		# then $MR->trim() each element in the array
		@param_names = map { $MR->trim($_) } @param_names;

		# make new array @output_names and separate from @param_names via [\w\@\{\}\']+\s+\bOUTPUT\b
		my @output_names = ();
		my @input_names = ();
		foreach my $param (@param_names)
		{
			if ($param =~ /([\w\@\{\}\']+)\s+\bOUTPUT\b/i)
			{
				push(@output_names, $1);
				push(@input_names, $1);
			}
			else
			{
				push(@input_names, $param);
			}
		}

		my $function_call = "";
		$function_call = $CFG{python_function_call} if $CFG{python_function_call};

		my $func_name = $stored_proc_name;
		$func_name =~ s/\./_/g;
		$function_call =~ s/\%PROC_NAME\%/$func_name/g;
		my $params = "";
		$params = ", " . join(", ", @input_names) if scalar(@input_names) > 0;
		$function_call =~ s/\%PARAMS\%/$params/g;

		$cont_str = $function_call;

		# comment exec calls out for now
		# $cont_str = "\"\"\"" . $cont_str . "\"\"\"";

		# remove all new lines from $cont_str
		$cont_str =~ s/\n//g;
	}

	@{$ar} = split(/\n/, $cont_str);
	return $ar;
}

sub cursor_def
{
	my $ar = shift;

	$ar = generic_substitution($ar, "cursor_def_pre_subst");

	my $cont_str = join("\n", @{$ar});
	$cont_str =~ s/\s*\bIS\b/__COLON__/i;

	if ($cont_str =~ /__COLON__/ && $cont_str !~ /\)\s*__COLON__/)
	{
		$cont_str =~ s/__COLON__/()__COLON__/;
	}

	$cont_str =~ s/__COLON__([\s\S]+)/:\n__TAB_ADD__inner_query = spark.sql(f\"\"\"$1\"\"\")\n__TAB_DEL__return inner_query/;
	$cont_str =~ s/(\=\s*)(\w+)(\s|;)/$1\{$2\}$3/g;  # for variables

	#if cursor is found, replace query name with cursor name
	my $df_name = "";

	# go through %PROC_VARIABLES and replace all instances of the variable name
	# with the variable type using $CFG{proc_variable_sql_wrapping} with %VARNAME% substitution

	if ($CFG{proc_variable_sql_wrapping})
	{
		foreach my $var (keys %PROC_VARIABLES)
		{
			my $var_type = $PROC_VARIABLES{$var};
			my $var_dec = $CFG{proc_variable_sql_wrapping};
			$var_dec =~ s/\%VARNAME\%/$var/g;
			$var_dec =~ s/\%VARTYPE\%/$var_type/g;
			$cont_str =~ s/\Q$var\E/$var_dec/g;
		}
	}

	# if "default_sql_wrapping" in config

	my @start_comments = ();
	while ($cont_str =~ /^(\s*)(__BB_COMMENT_[0-9]+__)(.*)/s)
	{
		push(@start_comments, $1.'"""'.$2.'"""'."\n");
		$cont_str = $3;
	}

	my $is_sql = 0;

	my $no_comment_cont_str = $cont_str;
	$no_comment_cont_str =~ s/__BB_COMMENT_[0-9]+__//gs;
	if ($no_comment_cont_str =~ /^\s*(\w+)\s*(\w*)/s)
	{
		my $first_sql_key = uc($1);
		my $second_sql_key = uc($2);

		if ($first_sql_key =~ /^\s*END\s*$/i)
		{
			$first_sql_key = $second_sql_key;
			$second_sql_key = $3 if $no_comment_cont_str =~ /^\s*(\w+)\s+(\w+)\s+(\w+)/s
		}

		if ($STAR_SQL_KEYWORDS{$first_sql_key} || $STAR_SQL_KEYWORDS{"$first_sql_key $second_sql_key"} || $STAR_SQL_KEYWORDS{"$first_sql_key $second_sql_key"})
		{
			$is_sql = 1;
		}
	}

	if (!$is_sql)
	{
        if($cont_str =~ /^\s*\bnull\b\s*\;?\s*$/is)
		{
			$cont_str = 'print("An exception occurred")';
		}
    }

	my $out = $cont_str;
	if ($CFG{default_sql_wrapping} && $is_sql)
	{

		$out = $CFG{default_sql_wrapping};
		$out =~ s/\%SQL\%/$cont_str/g;

		if ($df_name)
		{
			$out =~ s/\%DF\%/$df_name/g;
		}
		else
		{
			$out =~ s/\%DF\%/query_$df_name_number/g;
			$df_name_number++;
		}
	}

	$out = join("\n", @start_comments) . $out;

	if ($CFG{between_default_fragments} && $MR->trim($out) ne '')
	{
		# multiple separations may occur, this is ok for Databricks import
		$out = $CFG{between_default_fragments} . $out . $CFG{between_default_fragments};
	}

	@{$ar} = split(/\n/, $out);
	return $ar;
}

sub execute_immediate_fragment
{
	my $ar = shift;
	$ar = generic_substitution($ar, "execute_immediate_fragment");
   
	my $cont_str = join("\n", @{$ar});
	#$cont_str =~ s/(.*)\|\|\s*\'$/$1/is;
	my $out = '';
	if ($cont_str =~ /^\s*EXECUTE\s+IMMEDIATE\b\s*\((.*)\s*\)/is)
	{
        $out = $1;
    }	
	elsif($cont_str =~ /^\s*EXECUTE\s+IMMEDIATE\b\s*(.*)\s*/is)
	{
		$out = $1;
	}
	elsif($cont_str =~ /^\s*EXECUTE\b\s*(.*)\s*/is)
	{
		$out = $1;
	}
    $out =~ s/\'\'\'/'/g;
    $out =~ s/(?<![\'])\'\s*\|\|\s*(\w+)/{$1/g;
    $out =~ s/(\w+)\s*\|\|\s*\'/$1}/g;
    $out =~ s/\'\'/'/g;
	
    $out = "f\"\"$out\"\"\"";
    $out =~ s/f\"\"\'/f"""/;

    $out = "spark.sql($out)";

	@{$ar} = split(/\n/, $out);
	return $ar;
}

sub select_into_fragment
{
	my $ar = shift;
	$ar = generic_substitution($ar, "select_into_fragment");
   
	my $cont_str = join("\n", @{$ar});
	$cont_str =~ /\bSELECT\s+(.*?)\s*\bINTO\b\s*(.*?)\s*\bFROM\b/is;
	my $column_str = $1;
	my $variable_str = $2;
#	foreach my $col (split /\,/, $column_str)
#	{
#		$col = $MR->trim($col);
#		my $current_var = '';
#		if ($col =~ /(\w+)\s*\(/)
#		{
#            $current_var = 'v_'.lc($1);
#        }
#        else
#		{
#			$current_var = "v_$col";
#		}
#
#		if ($variable_str ne '')
#		{
#            $variable_str .= ',';
#        }
#        $variable_str .= $current_var;
#	}

#	if ($variable_str =~ /\,/)
#	{
#        $cont_str =~ s/\bINTO\b.*?\bFROM\b/FROM/is;
#    }
#	else
#	{
#		$cont_str =~ s/\bINTO\b\s+\w+\s*//is;
#	}
	
	$cont_str =~ s/\bINTO\b.*?\bFROM\b/FROM/is;
	$cont_str =~ /(.*)(\bSELECT\b.*)/is;
	my $per_query = $1;
	my $query = $2;
	my $variable_assignment_from_select_template = $CFG{variable_assignment_from_select};
	$variable_assignment_from_select_template =~ s/\%QUERY\%/$query/s;
	$variable_assignment_from_select_template =~ s/\%VARIABLES_STRING\%/$variable_str/s;

	if ($variable_str =~ /\,/)
	{
        $variable_assignment_from_select_template =~ s/\%IS_SINGLE\%//s;
    }
	else
	{
		$variable_assignment_from_select_template =~ s/\%IS_SINGLE\%/[0]/s;
	}

	my $out = $per_query.$variable_assignment_from_select_template;

	@{$ar} = split(/\n/, $out);
	return $ar;
}

sub default_handler
{
	my $ar = shift;

	my $cont_str = join("\n", @{$ar});

	if ($cont_str =~ /\bSELECT\b.*\bPIVOT\b/is)
	{
		$cont_str = convert_pivot_to_case_when($cont_str);
    }
	
	$cont_str =~ s/\bGO\b$//i;
	my $copy_cont = $cont_str;
	$copy_cont =~ s/__BB_COMMENT_[0-9]+__//gs;

	# if sql variable declaration is found, replace with None value
	if ($copy_cont =~ /^\s*(\w+)\s+\w+\.\w+\s*$/)
	{
		$cont_str =~ s/\s*(\w+)\s+(\w+\.\w+)\s*/# replaced $2 with None\n$1 = None/;
	}

	#if cursor is found, replace query name with cursor name
	my $df_name = "";

	# if ($CFG{keep_comments_in_place})
	# {
	# 	if ($cont_str =~ /(\s*CURSOR\s*(\w+).*?IS)/gis)
	# 	{
	# 		my $statement = $1;
	# 		$df_name = $2;
	# 		$cont_str =~ s/\Q$statement\E//is;
	# 	}
	# }
	# else
	# {
	# 	if ($cont_str =~ /(^\s*CURSOR\s*(\w+).*?IS)/gis)
	# 	{
	# 		my $statement = $1;
	# 		$df_name = $2;
	# 		$cont_str =~ s/\Q$statement\E//is;
	# 	}
	# }

	# go through %PROC_VARIABLES and replace all instances of the variable name
	# with the variable type using $CFG{proc_variable_sql_wrapping} with %VARNAME% substitution

	my %PROC_VARIABLES_AND_OTHERS = %PROC_VARIABLES;

	# add to %PROC_VARIABLES_AND_OTHERS if there exists $CFG{custom_var_regex_wrap}
	if (exists $CFG{custom_var_regex_wrap} && $CFG{custom_var_regex_wrap})
	{
		my $custom_var_regex_wrap = $CFG{custom_var_regex_wrap};
		while ($cont_str =~ /$custom_var_regex_wrap/gi)
		{
			$PROC_VARIABLES_AND_OTHERS{$1} = '__NO_TYPE__';
		}
	}

	if ($CFG{proc_variable_sql_wrapping})
	{
		foreach my $var (keys %PROC_VARIABLES_AND_OTHERS)
		{
			my $var_type = $PROC_VARIABLES_AND_OTHERS{$var};
			my $var_dec = $CFG{proc_variable_sql_wrapping};
			$var_dec =~ s/\%VARNAME\%/$var/g;
			$var_dec =~ s/\%VARTYPE\%/$var_type/g;
			$cont_str =~ s/\Q$var\E/$var_dec/g;
		}
	}

	# if "default_sql_wrapping" in config

	my @start_comments = ();
	while ($cont_str =~ /^(\s*)(__BB_COMMENT_[0-9]+__)(.*)/s)
	{
		push(@start_comments, $1.'"""'.$2.'"""'."\n");
		$cont_str = $3;
	}

	my $is_sql = 0;
	my $is_cte_sql = 0;

	my $no_comment_cont_str = $cont_str;
	$no_comment_cont_str =~ s/__BB_COMMENT_[0-9]+__//gs;
	$no_comment_cont_str =~ s/^\s*END\s*(\;|)\s*SELECT\b/SELECT/is;

	# is a CTE statement
	if ($CFG{convert_cte_to_tables} && ($no_comment_cont_str =~ /\bWITH\s+\w+\s+AS\s*\(\s*SELECT\b|\,\s+\w+\s+AS\s*\(\s*SELECT\b/is
										|| $no_comment_cont_str =~ /\bSELECT\b.*?\bINTO\s+\[?\`?\#\w+\`?\]?.*/is)
	   )
	{
		$is_sql = 1;
		$is_cte_sql = 1;
		#$MR->log_error($copy_cont);
	}
	elsif ($no_comment_cont_str =~ /^\s*(\w+)\s*(\w*)/s)
	{
		my $first_sql_key = uc($1);
		my $second_sql_key = uc($2);

		if ($first_sql_key =~ /^\s*END\s*$/i)
		{
			$first_sql_key = $second_sql_key;
			$second_sql_key = $3 if $no_comment_cont_str =~ /^\s*(\w+)\s+(\w+)\s+(\w+)/s
		}

		if ($STAR_SQL_KEYWORDS{$first_sql_key} || $STAR_SQL_KEYWORDS{"$first_sql_key $second_sql_key"})
		{
			$is_sql = 1;
		}
	}

	if (!$is_sql)
	{
        if($cont_str =~ /^\s*\bnull\b\s*\;?\s*$/is)
		{
			$cont_str = 'print("An exception occurred")';
		}

		# wrap multiline sql comments in the block
		$cont_str =~ s/(__BB_COMMENT_[0-9]+__)/\'\'\'$1\'\'\'/gis if $CFG{wrap_non_sql_comments_in_string};
    }
    
	my $out = $cont_str;
	if ($CFG{default_sql_wrapping} && $is_sql)
	{
		@{$ar} = split(/\n/, $cont_str);
		$ar = generic_substitution($ar, "default_sql_subst");
		$cont_str = join("\n", @{$ar});

		if ($cont_str =~ /\bDELETE\b\s+(\w+)\s+FROM\b\s+([\w\.]+)\s+AS\s+\1/is)
		{
			my $var = $1;
			my $true_val = $2;

			$cont_str =~ s/\bDELETE\b\s+\Q$var\E\s+FROM\b\s+\Q$true_val\E\s+AS\s+\Q$var\E/DELETE FROM $true_val/is;
			$cont_str =~ s/\Q$var\E\./$true_val./gis;
		}

		if ($cont_str =~ /\bDELETE\b\s+(\w+)\s+FROM\b\s+([\w\.]+)\s+\1\s+WHERE\b/is)
		{
			my $var = $1;
			my $true_val = $2;

			$cont_str =~ s/\bDELETE\b\s+\Q$var\E\s+FROM\b\s+\Q$true_val\E\s+\Q$var\E\s+WHERE\b/DELETE FROM $true_val WHERE/is;
			$cont_str =~ s/\Q$var\E\./$true_val./gis;
		}
		$cont_str =~ s/\bFULL\s+OUTER\s+JOIN\b/FULL_OUTER_JOIN_TEMPORARY_PLACEHOLDER/gi;
		$cont_str =~ s/\b(?!INNER|OUTER|LEFT|RIGHT|CROSS)\bJOIN\b/INNER JOIN/gi;
		$cont_str =~ s/FULL_OUTER_JOIN_TEMPORARY_PLACEHOLDER/FULL OUTER JOIN/gi;
		$cont_str =~ s/\bLEFT\s+INNER/LEFT/gis;
		$cont_str =~ s/\bOUTER\s+INNER/OUTER/gis;
		$cont_str =~ s/\bRIGHT\s+INNER/RIGHT/gis;
		$cont_str =~ s/\bCROSS\s+INNER/CROSS/gis;
		
		if($cont_str =~ /\bUPDATE\s+(\w+)\s+SET\b/is)
		{
			my $tbl = $1;
            if ($cont_str =~ /\bJOIN\s+(\w+\.?\w*\.?\w*)\s+(\w+)/is)
			{
				my $tbl_name = $1;
				my $tbl_alias = $2;
                if ($tbl eq $tbl_alias)
				{
                    $cont_str =~ s/\bUPDATE\s+\w+(\s+SET\b)/UPDATE $tbl_name $tbl_alias$1/is;
                }
            }
        }

		$cont_str = $CONVERTER->convert_update_to_merge($cont_str);
		#$MR->log_error($cont_str);
		$cont_str =~ s/\;\s*$//gis;

		# for cross apply
		if ($CFG{cross_apply_var_substitution})
		{
			if ($cont_str =~ /\%CROSS_VAR_[0-9]+\%/ && $cont_str =~ /\%CROSS_VAR_VALS\%/)
			{
				my $cross_var_vals = $1 if $cont_str =~ /\%CROSS_VAR_VALS\%\s*(\([\s\S]+?\))/;

				# remove ( and ) from front and back
				$cross_var_vals =~ s/^\s*\(//;
				$cross_var_vals =~ s/\)\s*$//;

				my @cross_var_vals = split(/\,/, $cross_var_vals);

				# for each trim
				@cross_var_vals = map { $MR->trim($_) } @cross_var_vals;

				# for each in @cross_var_vals replace %CROSS_VAR_1% with 0th element
				# and %CROSS_VAR_2% with 1st element and so on
				my $cross_var_counter = 1;
				foreach my $cross_var_val (@cross_var_vals)
				{
					$cont_str =~ s/\%CROSS_VAR_$cross_var_counter\%/$cross_var_val/g;
					$cross_var_counter++;
				}

				$cont_str =~ s/\%CROSS_VAR_VALS\%\s*(\([\s\S]+?\))//;
			}
		}
		
		$out = $CFG{default_sql_wrapping};

		if ($is_cte_sql)
		{
			my $table_name = "";
			$table_name = $1 if $cont_str =~ /\bWITH\s+(\w+)\s+AS\s*\(\s*SELECT\b/is;
			$table_name = $1 if $cont_str =~ /\,\s+(\w+)\s+AS\s*\(\s*SELECT\b/is;
			$table_name = $1 if $cont_str =~ /\bSELECT\b.*?\bINTO\s+\`?\#?(\w+)\`?/is;
			$out = $CFG{default_cte_sql_wrapping} if exists $CFG{default_cte_sql_wrapping};
			$out =~ s/\%CTE_TABLE\%/$table_name/g;
			$cont_str =~ s/\bWITH\s+\w+\s+AS\s*\(\s*SELECT\b|\,\s+\w+\s+AS\s*\(\s*SELECT\b/SELECT/is;
			$cont_str =~ s/\)([^)]*$)/$1/is;
			$cont_str =~ s/\bINTO\s+\`?\#?\w+\`?//is;
		}

		$cont_str =~ s/__BB_COMMENT_([0-9]+)__/__BB_SQL_COMMENT_$1__/gs;

		$out =~ s/\%SQL\%/$cont_str/g;

		if ($df_name)
		{
			$out =~ s/\%DF\%/$df_name/g;
		}
		else
		{
			$out =~ s/\%DF\%/query_$df_name_number/g;
			$df_name_number++;
		}
	}

	$out = join("\n", @start_comments) . $out;

	if ($CFG{between_default_fragments})
	{
		# multiple separations may occur, this is ok for Databricks import
		$out = $CFG{between_default_fragments} . $out . $CFG{between_default_fragments};
	}

	@{$ar} = split(/\n/, $out);

	return generic_substitution($ar, "sp_log_subst");
	#return $ar;
}

sub convert_merge_into
{
	my $ar = shift;
	my $sql = join("\n", @$ar);
	$MR->log_msg("convert_merge_into:\n$sql");
	$sql =~ s/(.*)\;$/$1/s;
	$sql = $MR->trim($sql);
	my $ret;
	if($sql =~ /(\bMERGE INTO\b.*?)(\s*\bWHEN NOT MATCHED.*?)(\s*\bWHEN MATCHED.*)/is)
	{
		$sql = $1.$3.$2;
	}
	if($sql =~ /\bOUTPUT\s+\$action\s+INTO\b\s+(\w+)/is)
	{
		my $tbl_name = $1;dsfsd
		
		$sql =~ s/\bOUTPUT\s+\$action\s+INTO\b\s+\w+/RETURNING\nCASE\nWHEN _change_type = 'update' THEN 'UPDATE'\nWHEN _change_type = 'insert' THEN 'INSERT'\nELSE 'No Change'\nEND AS action_type/is;

		$sql = $CONVERTER->convert_sql_fragment($sql);
		$ret = "$tbl_name = spark.sql(f\"\"\"$sql\"\"\")\n";
		$ret .= "$tbl_name.write.mode(\"append\").saveAsTable(\"$tbl_name\")\n";
	}
	else
	{
		$ret = "spark.sql(f\"\"\"$sql\"\"\")\n";
		$ret = $CONVERTER->convert_sql_fragment($ret);
	}
	@{$ar} = split(/\n/, $ret);
	return $ar;
}

sub remove_comments
{
	my $cont = shift;
	$cont =~ s/\-\-.*//gm;
	$cont =~ s/\/\*.*?\*\///gs;
	return $cont;
}

sub comment_fragment
{
	my $ar = shift;

	my $cont_str = join("\n", @{$ar});
	$cont_str =~ s/^\s*(.*)/# $1/gm;
	$cont_str = "# Please fix me\n".$cont_str;
	@{$ar} = split(/\n/, $cont_str);
	return $ar;
}

sub notebook_call
{
	my $ar = shift;

	my $cont_str = join("\n", @{$ar});
	$cont_str =~ /\bPERFORM\s+(\w+\.\w+)\(/is;
	@{$ar} = ("dbutils.notebook.run('$1')");
	return $ar;
}

sub convert_pivot_to_case_when
{
	my $cont_str = shift;
	if ($cont_str =~ /(.*)(\bSELECT\b.*)(\bPIVOT\s*\(.*)/is)
	{
		my $ret_val = '';
        my $pre = $1;
        my $select = $2;
        my $pivot = $3;
		
		my $columns;
		my $table;
		if ($select =~ /\bSELECT\b(.*)\bFROM\b(.*)/is)
		{
			$columns = $MR->trim($1);
			$table = $2;
        }
		if ($pivot =~ /\bPIVOT\s*\(\s*(\w+)\s*\(\s*(\w+)\s*\)\s*FOR\s+(\w+)\s+IN\s*\(\s*(.*?)\s*\)/is)
		{
			my $pivot_func = $1;
			my $agr_column = $2;
			my $case_when_column = $3;
			my $case_when_column_alias = $4;
			$ret_val = $pre."\nSELECT $columns";
			foreach(split(/\,/,$case_when_column_alias))
			{
				my $col = $MR->trim($_);
				$ret_val .= ",\n";
				$ret_val .="$pivot_func(CASE WHEN $case_when_column = '$col' THEN $agr_column ELSE 0 END) AS $col"
			}
			$ret_val .= "\nFROM $table\nGROUP BY\n$columns";
        }        
		return $ret_val;
    }

	return $cont_str;
}