use strict;
use List::Util qw(first);

my $CONVERTER;

sub init_shared_hooks
{
	my ($params) = @_;
	$CONVERTER = $params->{CONVERTER} unless $CONVERTER;
}

sub preprocess_delimit_statements
{
	my $self = $CONVERTER; #shift;
	my $lines = shift;
	my $args = shift || {};

	# pile up all expected keywords, both SQL and not, for easier matching
	my (@single_kw, %KW);
	if ($args->{keywords} && (ref($args->{keywords}) eq 'HASH')) # caller specifies complete keyword map
	{
		%KW = %{$args->{keywords}};
	}
	else
	{
		@single_kw = qw(IF FETCH WHILE INSERT DECLARE FOR DROP UPDATE DELETE EXEC EXECUTE CLOSE DEALLOCATE CREATE); # copied from SQLParser::preprocess_add_delimiters
		push(@single_kw, 'SET\s+\@\w+'); # copied from SQLParser::preprocess_add_delimiters
		if ($args->{keywords} && (ref($args->{keywords}) eq 'ARRAY')) # caller specifies supplemental list of non-SQL keywords
		{
			push(@single_kw, @{$args->{keywords}});
		}
		%KW = map { ($_ => 0) } @single_kw; # zero for non-SQL
		if ($Globals::ENV{CONFIG}->{sql_keywords})
		{
			$KW{$_} ||= 1 foreach @{$Globals::ENV{CONFIG}->{sql_keywords}}; # 1 for SQL, possibly updating zero
		}
	}
	@single_kw = sort { length($b) <=> length($a) } keys %KW;

	my $match_kwd = sub
	{
		my $str = shift;
		my $kwd = shift;
		my $ret;
		if ($kwd && ($str =~ /^\s*$kwd\b/i))
		{
			$ret = $kwd;
		}
		$ret ||= first { $str =~ /^\s*$_\b/i } @single_kw;
		#$self->debug_msg("match_kwd($str): returning $ret");
		return $ret;
	};

	my %select_combos = map { ($_ => 1) } qw(CREATE INSERT UNION);

	$Globals::ENV{PREPROCESS} ||= {};
	$Globals::ENV{PREPROCESS}->{MASKED} = { map { ($_ => []) } qw(comment string) }; # these need to be global so we can hold them out until just before fragment conversion
	my @stmts = ();
	my $frag = [];
	my $in_sql = '';
	while (@$lines)
	{
		#$self->debug_msg('Lines remaining: ' . scalar(@$lines));
		push(@$frag, shift(@$lines)); # a fragment is a set of one or more lines...
		#$self->debug_msg('open fragment: ' . Dumper($frag));
		my ($balanced, $chunks) = chunk_statement({parens => 1}, @$frag); # ...but we want to deal with sets of strings, comments, and/or interspersed code snippets
		#$self->debug_msg('open fragment chunks: ' . Dumper($chunks));

		my $frag_string = join("\n", @$frag);
		my $kwd;
		if (!$in_sql # if we weren't already in a SQL statement, and:
		    && @$chunks # we have content, and:
		    && !ref($chunks->[0]) # it doesn't start with a comment or string
		    )
		{
			if (!($kwd = $match_kwd->($frag_string))) # it doesn't start with a keyword
			{
				$kwd = $match_kwd->($frag_string, 'ELSE'); # check for the special case that is "else"
			}
			elsif ($KW{$kwd}) # it's a SQL keyword
			{
				$in_sql = $kwd; # we're in a SQL statement
			}
		}
		my ($next_chunks, $next_start);
		if (@$lines) # peek at next line
		{
			$next_chunks = chunk_statement({parens => 1}, $lines->[0]);
			#$self->debug_msg('next line chunks: ' . Dumper($next_chunks));
			$next_start = $next_chunks->[0];
		}
		if (!defined($next_start) # no next line, or:
		    || ($balanced # this line is balanced, and:
			&& !ref($next_start) && ($kwd = $match_kwd->($lines->[0], ($in_sql ? '' : 'ELSE'))) # next line starts with a keyword, and:
			&& ($KW{$kwd} # if it's SQL:
			    ? (!$in_sql # we're not already in SQL, or:
			       || !$select_combos{uc($in_sql)} || (lc($in_sql = $kwd) ne 'select') # we're not in a special combo SQL statement (but don't let it add multiple selects)
			       )
			    : ((lc($kwd) ne 'begin') || ($frag_string !~ /^\s*(?:CREATE(?:\s+OR\s+REPLACE)?|REPLACE)\s+PROC/is)) # if it's non-SQL, we're not finishing a procedure declaration
			    )
			)
		    )
		{
			# inject a semi-colon (if not already present) between last meaningful chunk and any trailing comment/whitespace
			my @tail;
			while (@$chunks)
			{
				# pop off and collect whitespace and comments
				my $last_chunk = pop(@$chunks);
				if (ref($last_chunk)
				    ? ($last_chunk->[0] =~ /^['"]$/) # not a comment
				    : $last_chunk =~ /\S/s # not just whitespace
				    )
				{
					push(@$chunks, $last_chunk);
					push(@$chunks, ';') unless $last_chunk =~ /;\s*$/;
					last;
				}
				else
				{
					# fix weird Sybase comment style
					if (ref($last_chunk) && ($last_chunk->[0] eq '//'))
					{
						$last_chunk->[0] = '--';
					}
					unshift(@tail, $last_chunk);
				}
			}
			# add back any collected whitespace/comments
			while (@tail)
			{
				my $last_chunk = shift(@tail);
				push(@$chunks, $last_chunk);
			}
			#$self->debug_msg('semi added chunks: ' . Dumper($chunks));
			# flatten the fragment so we can re-chunk it to mask comments and strings
			my $chunk_string = join('', map { (ref($_) ? @$_ : $_) } @$chunks);
			$frag = chunk_statement({
				comments => $Globals::ENV{PREPROCESS}->{MASKED}->{comment},
				strings => $Globals::ENV{PREPROCESS}->{MASKED}->{string},
				parens => 1,
			}, $chunk_string);
			#$self->debug_msg('CHUNK: ' . Dumper($frag));
			# add this statement to the stack and reset for the next one
			push(@stmts, $frag->[0]);
			$frag = [];
			$in_sql = '';
		}
		# else, keep adding more content to this fragment until it's complete or we run out of lines
	}
	#$self->debug_msg('STATEMENTS: ' . Dumper(\@stmts));
	return @stmts;
}

sub chunk_statement
{
	my $self = $CONVERTER; #shift;
	my $args = shift || {};
	my $sql = join("\n", @_);
	my $even = 1;
	my @ret = ();
	if ($sql !~ /\S/s) # empty string or just whitespace is an easy out
	{
		push(@ret, $sql);
	}
	else
	{
		# these are our sane defaults in case none are configured
		my $quotes_regex = q{['"]};
		my %comment_pairs = (
			'--' => "\n",
			'/' => '*/',
		);
		my %paren_pairs = (
			'(' => ')',
		);
		if (my $delim_config = $self->{CONFIG}->{stmt_chunk_delimiters})
		{
			$quotes_regex = $delim_config->{quotes_regex} if exists $delim_config->{quotes_regex};
			%comment_pairs = %{$delim_config->{comment_pairs}} if exists $delim_config->{comment_pairs};
			%paren_pairs = %{$delim_config->{paren_pairs}} if exists $delim_config->{paren_pairs};
		}
		my $delim_match = join('|', $quotes_regex, map { "\Q$_\E" } %comment_pairs);
		my $parens;
		if ($args->{parens}) # caller wants to check if parens are balanced
		{
			$parens = join('|', map { "\Q$_\E" } %paren_pairs);
			$delim_match .= '|' . $parens;
			$parens = '(?:' . $parens . ')';
		}
		my (@buf, @chunk, $match_this);
		my $open_paren = 0;
		while ($sql =~ m@\G(.*?(?!<\\))((?:$delim_match)+)@cgs) # find unescaped delimiters and any content that precedes them
		{
			my ($content, $delims) = ($1, $2);
			while ($delims =~ /\G($delim_match)/cgs) # in case we have multiple consecutive delims
			{
				my $delim = $1;
				if (!$match_this) # no open string or comment
				{
					push(@buf, $content);
					if (exists $comment_pairs{$delim}) # is an unescaped comment opener
					{
						$match_this = $comment_pairs{$delim}; # wait for comment closer
						push(@chunk, $delim);
					}
					elsif ($delim =~ /^$quotes_regex$/) # is an unescaped quote
					{
						$match_this = $delim; # string is now open
						push(@chunk, $delim);
					}
					else # parens and closing delimiters are normal content if no comment or string is open
					{
						if ($parens && ($delim =~ /^$parens$/)) # is an unescaped paren
						{
							$open_paren += (exists $paren_pairs{$delim}) ? 1 : -1;
						}
						push(@buf, $delim);
					}
				}
				elsif ($delim eq $match_this) # matching quote/closer
				{
					if ($delim eq "\n") # keep comment-ending newline separate from comment
					{
						push(@chunk, $content);
						push(@buf, [@chunk], $delim);
					}
					else
					{
						push(@chunk, $content, $delim);
						push(@buf, [@chunk]);
					}
					$match_this = ''; # string/comment is now closed
					@chunk = ();
				}
				else # open string or comment
				{
					push(@chunk, $content, $delim); # keep all string/comment content, even if it looks like a delimiter
				}
				# if we have multiple consecutive delims, there is no content between them
				$content = '';
			}
		}
		if ($sql =~ /\G(.+)$/cgs) # don't forget any trailing content...
		{
			my $content = $1;
			if ($match_this) # open string or comment
			{
				push(@chunk, $content);
			}
			else
			{
				push(@buf, $content);
			}
		}
		if (@chunk)
		{
			push(@buf, [@chunk]);
			@chunk = ();
			if ($match_this eq "\n") # EOL matches newline
			{
				$match_this = ''; # comment is now closed
			}
		}
		if ($match_this || ($parens && $open_paren)) # something left unmatched
		{
			$even = 0;
		}
		if ($args->{comments} || $args->{strings}) # caller wants comments and/or strings separated from other content
		{
			my %masks = (
				# these are our sane defaults in case none are configured
				comment => '/*BB*C%s**/',
				string => '"__BB_S%s__"',
			);
			if ($self->{CONFIG}->{mask_parts_make})
			{
				foreach my $part (keys %masks)
				{
					next unless ref $args->{"${part}s"}; # nothing more to do if caller doesn't want this part masked
					if ($self->{CONFIG}->{mask_parts_make}->{$part} && $self->{CONFIG}->{mask_parts_make}->{$part}->{make})
					{
						$masks{$part} = $self->{CONFIG}->{mask_parts_make}->{$part}->{make};
					}
				}
			}
			$sql = '';
			while (@buf)
			{
				my $chunk = shift(@buf);
				if (ref $chunk)
				{
					my ($delim, @rest) = @$chunk;
					$chunk = join('', $delim, @rest);
					if (exists $comment_pairs{$delim}) # comment
					{
						if (ref $args->{comments}) # caller wants comments collected and replaced by placeholder
						{
							my $idx = scalar(@{$args->{comments}});
							push(@{$args->{comments}}, $chunk);
							$chunk = sprintf($masks{comment}, $idx);
						}
						else # caller just wants comments removed
						{
							next;
						}
					}
					else # string
					{
						if (ref $args->{strings}) # caller wants strings collected and replaced by placeholder
						{
							my $idx = scalar(@{$args->{strings}});
							push(@{$args->{strings}}, $chunk);
							$chunk = sprintf($masks{string}, $idx);
						}
						else # caller just wants strings removed
						{
							next;
						}
					}
				}
				$sql .= $chunk;
			}
			push(@ret, $sql);
		}
		else
		{
			@ret = @buf;
		}
	}
	return ($even, \@ret) if (wantarray);
	return \@ret;
}

sub convert_and_unmask_fragment
{
	my $self = $CONVERTER; #shift;
	my $frag = shift;

	my $params = {};
	my ($MASKS, $MASKED, @masked_parts);
	if (($MASKS = $self->{CONFIG}->{mask_parts_make}) # masks are configured
	    && $Globals::ENV{PREPROCESS} && ($MASKED = $Globals::ENV{PREPROCESS}->{MASKED}) # it looks like we masked stuff during preprocessing
	    && (@masked_parts = grep { $MASKS->{$_} && $MASKS->{$_}->{make} && $MASKED->{$_} && @{$MASKED->{$_}} } keys %$MASKS) # we definitely used these masks
	    )
	{
		$params->{STATEMENT_CATEGORY} = $self->categorize_statement(join("\n", @$frag)); # categorize before unmasking
		foreach my $part (@masked_parts)
		{
			my $match;
			if (exists $MASKS->{$part}->{match})
			{
				$match = $MASKS->{$part}->{match};
			}
			else
			{
				$match = make_mask_match_regex($MASKS->{$part}, 'capture');
			}
			foreach (@$frag)
			{
				$_ =~ s/$match/$MASKED->{$part}->[$1]/eg;
			}
		}
	}

	$self->{called_within} = 1;
	my $res = $self->convert_sql_fragment(@$frag, $params);
	$self->{called_within} = 0;
	return $res;
}

sub make_mask_match_regex
{
	my $self = $CONVERTER; #shift;
	my $mask = shift;
	my $capturing = shift;
	if (!ref $mask)
	{
		my $which = $mask;
		unless ($self->{CONFIG}->{mask_parts_make} && ($mask = $self->{CONFIG}->{mask_parts_make}->{$which}))
		{
			return '';
		}
	}
	my $idx_match = '[0-9]+';
	$idx_match = '(' . $idx_match . ')' if $capturing;
	my ($before, $after) = split(/\%s/, $mask->{make}, 2); # split complete pattern where index would be injected
	my $regex = quotemeta($before) . $idx_match . quotemeta($after); # put it back together with numeric match in place of index
	return $regex;
}
