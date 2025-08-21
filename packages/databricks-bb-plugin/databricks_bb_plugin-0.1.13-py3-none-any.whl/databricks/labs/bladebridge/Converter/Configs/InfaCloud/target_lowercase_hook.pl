use strict;

my $MR = undef;
my $WRITER = undef;

sub init_run
{
	my $p = shift;
	$MR = $p->{MR}; #pointer to MiscRoutines class
	$WRITER = $p->{WRITER}; #pointer to SQL generator class
	$MR->debug_msg("Init called for job $p->{NAME}. Writer: $WRITER");
}

sub special_handle_TARGET
{
	my $node = shift;
	my $normal_out = $WRITER->generate_TARGET($node);

	# lowercase target column alias names
	#$normal_out =~ s/\.\s*alias\s*\(\s*\'(\w+)\'\s*\)/".$1.alias('" . lc($1) . "')"/ge;
	# $normal_out =~ s/\.\s*alias\s*\(\s*(\'\w+\')\s*\)/".alias(" . lc($1) . ")"/ge;
	# lowercase target table names
	$normal_out =~ s/\.\s*saveAsTable\s*\(\s*f'([\w\{\}\.]+)'\s*\,/".saveAsTable(f'" . lc($1) . "',"/ge;

	return $normal_out;

}

sub special_handle_JOINER
{
	my $node = shift;
	my $normal_out = $WRITER->generate_JOINER($node);

	# lowercase target column alias names
	$normal_out =~ s/\w+\.\s*alias\s*\(\s*\'(\w+)\'\s*\)/"" . lc($1) . ".alias('" . lc($1) . "')"/ge;
	# $normal_out =~ s/\.\s*alias\s*\(\s*\'(\w+)\'\s*\)/".$1.alias('" . lc($1) . "')"/ge;
	# $normal_out =~ s/\.\s*alias\s*\(\s*(\'\w+\')\s*\)/".alias(" . lc($1) . ")"/ge;
	# lowercase target table names
	# $normal_out =~ s/\.\s*saveAsTable\s*\(\s*f'([\w\{\}\.]+)'\s*\,/".saveAsTable(f'" . lc($1) . "',"/ge;

	return $normal_out;

}