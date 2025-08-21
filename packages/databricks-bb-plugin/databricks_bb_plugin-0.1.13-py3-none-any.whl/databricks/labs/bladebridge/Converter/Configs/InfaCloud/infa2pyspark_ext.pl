use strict;
# use Common::MiscRoutines;
# use DWSLanguage; 
# use Data::Dumper;
#use CodeGeneration::PySpark; 

my $mr = new Common::MiscRoutines();
my $LAN = new DWSLanguage(); 


sub convert_decode 
{
	my $expr = shift; 
	$mr->log_msg("STARTING DECODE CONVERSION $expr");

	#print("convert_decode subroutine was reached\n");

	$expr =~ /DECODE\s*\((.*)\)$/is;
	my $param = "($1)";
	$mr->log_msg("DECODE PARAMS: $param");

	my @args = $mr->get_direct_function_args($param);

	#Check if even or odd because first argument not required

	$mr->log_msg("DECODE ARGS " . Dumper(\@args));
	my $idx = 0; 

	my $ret = '';
	while ($idx < $#args - 1)
	{
		if(!$idx)
		{
			$ret .= "when($args[0] \= ($args[$idx+1]),$args[$idx+2])";
		}
		else 
		{
			$ret .= ".when($args[0] \= ($args[$idx+1]),$args[$idx+2])";
		}
		$idx = $idx + 2;
	}

	#if number of elements is even then add optional default arg
	my $odd_check = scalar(@args) % 2 ;
	if(!$odd_check)
	{
		$ret .= ".otherwise($args[$#args])";

	}

	$mr->log_msg("FINAL CONVERSION DECODE ARGS:$#args & $odd_check:\n $ret");
	return $ret;
}

sub convert_decode_if
{
    my $expr = shift;
    $mr->log_msg("STARTING DECODE IF CONVERSION $expr");

    # Extract the parameters inside the DECODE function
    $expr =~ /DECODE\s*\((.*)\)$/is;
    my $param = "($1)";
    $mr->log_msg("DECODE PARAMS: $param");

    # Assuming get_direct_function_args is a method to parse the parameters correctly
    my @args = $mr->get_direct_function_args($param);

    $mr->log_msg("DECODE ARGS " . Dumper(\@args));
    my $idx = 1;  # Start from the second element since the first is the value being compared

    my $ret = '';
    my $indent = '';
	my $base_indent = '';

    while ($idx < $#args)
	{
        if ($idx == 1)
		{
            $ret .= "${indent}IF($indent$args[$idx-1] = $args[$idx],$indent$args[$idx+1],";
        }
		else
		{
            $ret .= "$indent" . "IF($indent$args[$idx-1] = $args[$idx],$indent$args[$idx+1],";
        }
        $idx += 2;
        $indent .= "";
    }

	# Check if the number of elements is even to add optional default argument
    my $odd_check = scalar(@args) % 2;
    if (!$odd_check)
	{
        $ret .= "$indent$args[$#args]" . $base_indent . ')' x (($#args - 1) / 2) . "";
    }
	else
	{
        $ret .= "$indent" . "$args[$#args]" . ')' x ((($#args - 1) / 2) + 1) . "";
    }

    $mr->log_msg("FINAL CONVERSION DECODE ARGS:$#args:\n $ret");
    return $ret;
}