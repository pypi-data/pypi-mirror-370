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

sub preprocess_oracle_to_mysql_header
{
	my $cont = shift;

	my $oracle_file = join("\n", @$cont);
	my $oracle_procedure = $1 if $oracle_file =~ /(\bCREATE[\s\S]+?BEGIN\b)/i;
	my $original_procedure_header = $oracle_procedure;
    my $procedure_name;
    my @declarations;

    # Extract the procedure name
    $procedure_name = $1 if ($oracle_procedure =~ /CREATE\s+OR\s+REPLACE\s+PROCEDURE\s+(\w+)/i);

    # Extract the variable declarations
    while ($oracle_procedure =~ /(\w+)\s+(\w+)\s*(\(\d+\))?;/gi)
	{
        my $var_name = $1;
        my $var_type = $2;

        push @declarations, "  DECLARE $var_name $var_type;";
    }

    # Combine into MySQL procedure declaration
    my $mysql_procedure = "DELIMITER \$\$\n\nCREATE PROCEDURE $procedure_name()\nBEGIN\n";
    $mysql_procedure .= join("\n", @declarations) . "\n";
	$oracle_file =~ s/\Q$original_procedure_header\E/$mysql_procedure/i if $oracle_procedure;

    return $oracle_file;
}

sub preprocess_oracle_procedures
{
	my $cont = shift;
	
	my $cont_str = join("\n", @$cont);
	my $trn_control_flag = 0;

	if ($cont_str =~ /(\bCOMMIT\b|\bROLLBACK\b)/gis)
	{
		$trn_control_flag = 1; #transaction control statements are present.
	}

	$MR->log_msg("Beginning oracle preprocess. Transaction control enabled: $trn_control_flag, use_explicit_transactions flag: " . $CFG_POINTER->{use_explicit_transactions});
	if ($trn_control_flag && $CFG_POINTER->{use_explicit_transactions})
	{
		adjust_COMMIT_pattern('to_commit_begin')
	}
	else
	{
		adjust_COMMIT_pattern('to_commit')
	}

	my $process = 0; 
	#only preprocessing everything before BEGIN statement
	# foreach my $ln (@$cont)
	# {
	# 	if ($ln =~ /^\s*BEGIN\s*$/)
	# 	{
	# 		if ($CFG_POINTER->{use_explicit_transactions})
	# 		{
	# 			$ln .= "\n\%POST_FIRST_BEGIN\%;\n";
	# 		}
	# 		else
	# 		{
	# 			$ln = '%BEGIN_PROC%';
	# 		}
	# 		last;
	# 	}
	# 	$MR->log_msg("Line : " . Dumper($ln)); 

	# 	$ln =~ s/(\w+)\s+OUT\b/OUT $1/gi;
	# 	$ln =~ s/(\w+)\s+IN\b/ $1/gi;
	# 	$ln =~ s/\:\=/ DEFAULT/gi;
	# 	if ($ln =~ m/(\w+)\s+(INTEGER|VARCHAR2|NUMBER|DATE)(.*)/ && $ln !~ m/\,/)
	# 	{
	# 		$ln = "DECLARE $1 $2 $3";
	# 	}
	# }
	if ($cont_str =~ m{\b(CREATE|REPLACE|CREATE\s+OR\s+REPLACE)\s+PROCEDURE\s}i)
	{
		$cont_str =~ s{(\s+PROCEDURE\s+[\w.]+\s*\(.*?\)\s*\b)(AS|IS)\s+(.*?)(\s+BEGIN\b)}{"$1\n" . procedure_pre_begin($3)}sei;
		$cont_str =~ s{(\s+PROCEDURE\s+[\w.]+\s*\()(.*?)\)}{$1 . proc_args($2) . ")"}sei;

		if ($CFG_POINTER->{procedure_schema_name})
		{
			$cont_str =~ s{(\s+PROCEDURE\s+)(\w+)\.}{$1$CFG_POINTER->{procedure_schema_name}.}i or
			$cont_str =~ s{(\s+PROCEDURE\s+)(\w+)}{$1$CFG_POINTER->{procedure_schema_name}.$2}i;
		}
	}

	@$cont = split(/\n/, $cont_str);
	return @$cont;
}
sub procedure_pre_begin
{
	my $pre_begin = shift;
	$pre_begin =~ s{(\w+\s+(INTEGER|VARCHAR2|NUMBER|DATE)\b\s*.*?);}{DECLARE $&}sgi;
	$pre_begin =~ s{:=}{DEFAULT}g;
	if ($CFG_POINTER->{use_explicit_transactions})
	{
		$pre_begin .= "\n%BEGIN_PROC%\n\%POST_FIRST_BEGIN\%;\n";
	}
	else
	{
		$pre_begin .= "\n%BEGIN_PROC%\n";
	}
	return $pre_begin;
}
sub proc_args
{
	my $proc_args = shift;

	# NOTE: We are currently REMOVING the "IN" / "OUT" / "INOUT", but thast might not be right, 
	# so leaving the original line commented oput here
	# $proc_args =~ s{(\w+)\s+(IN|OUT|INOUT)\b}{$2 $1}g;
	$proc_args =~ s{(\w+)\s+(IN|OUT|INOUT)\b}{$1 }g;

	return $proc_args;
}

# depending on whether explicit begin is required or not, adjust config pattern
sub adjust_COMMIT_pattern
{
	my $to_pattern = shift;
	$MR->log_msg("adjust_COMMIT_pattern called with '$to_pattern'");
	return unless $CFG_POINTER->{line_subst};
	foreach my $el (@{$CFG_POINTER->{line_subst}})
	{
		next unless $el->{$to_pattern};
		$MR->log_msg("Found COMMIT element $el->{from}! Changing 'to' to $el->{$to_pattern}");
		$el->{to} = $el->{$to_pattern};
	}
}

sub init_hooks #register this function in the config file
{
	my $param = shift;
	%CFG = %{$param->{CONFIG}};
	$CFG_POINTER = $param->{CONFIG}; #give the ability to modify config incrementally
	$CONVERTER = $param->{CONVERTER};
	$MR = new Common::MiscRoutines unless $MR;
	#print "INIT_HOOKS Called. MR: $MR. config:\n" . Dumper(\%CFG);

}

sub post_conversion_adjustment
# This should be called via the "post_conversion_adjustment_hook" config tag
{
	my $everything = shift;
	my $cont = $everything->{CONTENT};
	my $cont_str = join("\n", @$cont);

	if ($everything->{CONFIG}->{post_conversion_subst}) 
	{
		foreach my $gsub (@{ $everything->{CONFIG}->{post_conversion_subst}  })
		{

			# NOTE: We are doing the below substitutions on the ENTIRE content, at once
			my $save_cont_str = $cont_str;
			my $eval_gsub = "my \$gsub_count = 0; 
			while (\$cont_str =~ s{$gsub->{from}}{$gsub->{to}}sgi) {
				die \"post_conversion_subst stuck in loop!!\" if \$gsub_count++ > 1000
			}";
			eval ($eval_gsub);
			my $ret = $@;
			if ($ret)
			{
				$MR->log_msg("Got stuck in loop; reverting to global change instead of \"while...\"");
				$cont_str = $save_cont_str;
				$eval_gsub = "my \$gsub_count = 0; 
				\$cont_str =~ s{$gsub->{from}}{$gsub->{to}}sgi;";
				eval ($eval_gsub);
				my $ret = $@;

				if ($ret)
				{
					$MR->log_error("************ EVAL ERROR in global substitution: $ret ************");
					$MR->log_error("*** Failing eval code: $eval_gsub");
					$MR->log_error("*** Input to substitution (\$cont_str): $cont_str\n");
					exit -1;
				}
			}
		}
	}
	@$cont = split(/\n/, $cont_str);
	return $cont;
}
