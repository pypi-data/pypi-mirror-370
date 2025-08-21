use strict;
use Data::Dumper;
use Common::MiscRoutines;
use DWSLanguage;


my $MR = new Common::MiscRoutines;

sub preprocess_re_convert_python
{
	my $cont = shift;

	$MR->log_msg("Ahold_re_convert_python.pl: Called preprocess_re_convert_python");

	my $cont_str = join("\n", @{$cont});

	my $regex_match = '\bCREATE\s*OR\s*REPLACE\s*TABLE\s*[\w\.]+\s*AS[\s\S]+?\-\-\s*OPTION\s*\(\s*LABEL\s*\=\s*\'[\w\s]+\'\s*\)\s*\;\s*\-\-.*';
	my $regex_match_2 = '\bCREATE\s*OR\s*REPLACE\s*TABLE\s*[\w\.]+\s*AS[\s\S]+?\-\-\s*OPTION\s*\(\s*LABEL\s*\=\s*\'[\w\s]+\'\s*\)\s*\;';
	# place all matches in an array
	my @matches = $cont_str =~ /$regex_match/gi;

	# add $regex_match_2 to matches
	push(@matches, $cont_str =~ /$regex_match_2/gi);

	# for each match, remove match if it contains INSERT INTO
	foreach my $match (@matches)
	{
		if ($match =~ /(\bINSERT\s*INTO\b|\DELETE\s*FROM\b)/)
		{
			$cont_str =~ s/\Q$match\E//gi;
		}
	}

	# my $count = 0;
	# foreach my $match (@matches)
	# {
	# 	if ($match =~ /(\bINSERT\s*INTO\b|\DELETE\s*FROM\b)/)
	# 	{
	# 		# $cont_str =~ s/\Q$match\E//g;
	#
	# 		# remove from array
	# 		splice(@matches, $count, 1);
	# 	}
	#
	# 	$count++;
	# }

	# sort matches by size
	@matches = sort { length($b) <=> length($a) } @matches;

	# for each match, create a new substitution and replace back into the content
	foreach my $match (@matches)
	{
		my $new_match = $match;

		my $label_comment = "";
		$label_comment = $2 if $match =~ /(\-\-\s*OPTION\s*\(\s*LABEL\s*\=\s*\'[\w\s]+\'\s*\)\s*\;)(\s*\-\-.*)/i;

		$new_match =~ s/(\-\-\s*OPTION\s*\(\s*LABEL\s*\=\s*\'[\w\s]+\'\s*\)\s*\;)\s*(\-\-.*)//gi;
		$new_match =~ s/(\-\-\s*OPTION\s*\(\s*LABEL\s*\=\s*\'[\w\s]+\'\s*\)\s*\;)//gi;

		my $label = "";
		$label = $1 if $match =~ /\-\-\s*OPTION\s*\(\s*LABEL\s*\=\s*\'([\w\s]+)\'\s*\)\s*\;/i;

		$new_match =~ s/(\bCREATE\s*OR\s*REPLACE\s*TABLE\s*[\w\.]+)\s*AS\b/$1\n\t\tTBLPROPERTIES ('label' = '$label')$label_comment\n\t\tAS/gis;

		$cont_str =~ s/\Q$match\E/$new_match/g;
	}

	@{$cont} = split(/\n/, $cont_str);
	return @{$cont};
}