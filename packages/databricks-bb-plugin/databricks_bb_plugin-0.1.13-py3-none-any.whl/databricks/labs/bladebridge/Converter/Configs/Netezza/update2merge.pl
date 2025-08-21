use strict;
use Data::Dumper;
use Common::MiscRoutines;
use DWSLanguage;
#use Math::Cartesian::Product;
no strict 'refs';



my $MR = new Common::MiscRoutines(MESSAGE_PREFIX => 'DBRKS_HOOKS');
my $LAN = new DWSLanguage();
my %CFG = (); #entries to be initialized
my $CFG_POINTER = undef;
my $CONVERTER = undef;
my $EXTERNAL_READ_FILE_TEMPLATE = undef;
my $EXTERNAL_READ_FILE_TEMPLATE_ROWID = undef;
my $EXTERNAL_WRITE_FILE_TEMPLATE = undef;
my $FILENAME = '';
my %PRESCAN = ();
my $CONVERT_TEMP=0;
my $TRIM=0;
my $FILE_EXTENSION ='';
my $sql_parser;


sub update_to_merge {
    my $ar = shift;
    my $str_content = join( "\n", @{$ar} );

    # $str_content = trim_char_columns($str_content);
    my @updates_withou_aliases = $str_content =~ /update\s+\w*\.*\w+\s+SET\s+.*?(?:\=|\|)\s*\w*\.*\w+\s+FROM\s+\w+s*\,.*?where.*?\;/gis;

    if ( scalar @updates_withou_aliases != 0 ) {
        for my $upd (@updates_withou_aliases) {
            my ($source) = $upd =~ /update\s+\w*\.*\w+\s+SET\s+.*?(?:\=|\|)\s*\w*\.*\w+\s+FROM\s+(\w+\s*\w+\s*\,.*?)where.*?\;/gis;
            my $orig_source = $source;
            $source =~ s/(\w+)/$1 $1/gis;
            my $new_upd = $upd;
            $new_upd =~ s/\Q$orig_source\E/$source/gis;
            $str_content =~ s/\Q$upd\E/$new_upd/gis;
        }
    }



    my @updates1 = $str_content =~/update\s+\w*\.*\w+\s+\w+\s*SET\s+.*?(?:\=|\|)\s*\w*\.*\w+\s+FROM\s+\w+\b\s*\b\w+\b\s*\,.*?where.*?\;/gis;

    if ( scalar @updates1 != 0 ) {

        for my $upd (@updates1) {
            my ( $target, $tals, $set, $source, $condition ) = $upd =~/update\s+(\w*\.*\w+)\s+(\w+)\s+(SET\s+.*?(?:\=|\|)\s*\w*\.*\w+\s+)FROM\s+(\w+\s*\w+\s*\,.*?)where(.*?)\;/gis;

            my $orig_cond = $condition;
            my @aliases   = $source =~ /\w+\s+(\w+)/gis;

            #$MR->log_err($condition);
            my @target_conditions = $condition =~ /\Q$tals\E\.\w+/gis;
            @target_conditions = uniq(@target_conditions);
            $source            = $target . " " . $tals . ",\n" . $source;

  
            my @conditions_to_move  = ();
            my @conditions_to_move2 = ();
            for my $al (@aliases) {
                my @cond_to_move = $condition =~ /\Q$al\E\.\w+/gis;
                for my $c (@cond_to_move) {
                    push( @conditions_to_move, $c );
                }
                my @cond_to_move2 = $set =~ /\Q$al\E\.\w+/gis;
                for my $c (@cond_to_move2) {
                    push( @conditions_to_move, $c );
                }

            }
            my @cond_to_move3 = "$set" =~ /\=\s*(\w+\b)(?!\.)(?!\()/gis;
            for my $c (@cond_to_move3) {
                push( @conditions_to_move2, $c );
            }
            my @cond_to_move3 = "$set" =~ /\|\s*(\w+\b)(?!\.)(?!\()/gis;
            for my $c (@cond_to_move3) {
                push( @conditions_to_move2, $c );
            }

            my $conds2 = join( "\n", uniq(@conditions_to_move2) );
            my $conds  = join( "\n", uniq(@conditions_to_move) );
            my @columns  = $conds =~ /\w+\.\w+/gis;
            my @columns2 = $conds2 =~ /\w+/gis;
            my $sl_col   = join( "\,\n", @columns );
            my $sl_col2  = join( "\,\n", @columns2 );
            $sl_col =~ s/(\w+)\.(\w+)/$1.$2 $1_$2/gis;
            $sl_col2 =~ s/(\w+)\.(\w+)/$1.$2 $1_$2/gis;

            #$sl_col =~ s/(\w+)\.(\w+)/$1.$2 $1_$2/gis;
            my $target_columns = join( "\,\n", uniq(@target_conditions) );
            $target_columns =~ s/(\w+)\.(\w+)/$1.$2 $1_$2/gis;
            my $where = '';
            if ( $sl_col2 eq '' ) {
                $where =
                    "( SELECT DISTINCT \n"
                  . $target_columns . ",\n"
                  . $sl_col
                  . "\nFROM "
                  . $source . " "
                  . " where\n"
                  . $condition
                  . ") source";
            }
            else {
                $where =
                    "( SELECT DISTINCT \n"
                  . $target_columns . ",\n"
                  . $sl_col . "\n,"
                  . $sl_col2
                  . "\nFROM "
                  . $source
                  . " where \n"
                  . $condition
                  . ") source";
            }

            # for my $al (@aliases)
            # {
            # 	 $condition =~ s/(\Q$al\E)\.(\w+)/source.$1_$2/gis;
            # 	 $set =~ s/(\Q$al\E)\.(\w+)/source.$1_$2/gis;
            # }
            my $on = '';
            for my $tcon (@target_conditions) {
                my ($src_con) = $tcon =~ /\Q$tals\E\.(\w+)/gis;
                $on =
                    $on
                  . "\nsource."
                  . $tals . "_"
                  . $src_con . " = "
                  . $tcon . " AND ";

            }
            $on = $on . ";";
            $on =~ s/and\s+\;//gis;

            # my $on = join("\,",uniq( @target_conditions));
            $set =~ s/(\w+)\.(\w+)/$1_$2/gis;
            my $final_sql =
                "MERGE INTO "
              . $target . " "
              . $tals
              . "\n USING \n"
              . $where
              . " ON \n"
              . $on
              . "\nWHEN MATCHED THEN UPDATE \n"
              . $set . ";";



            $final_sql = $sql_parser->convert_sql_fragment($final_sql);

            return $final_sql;
        }
    }
    my @updates = $str_content =~/update\s+\w*\.*\w+\s+SET\s+.*?(?:\=|\|)\s*\w*\.*\w+\s+FROM\s+\w+\b\s*\b\w+\b\s*\,.*?where.*?\;/gis;
    if ( scalar @updates != 0 ) {

        for my $upd (@updates) {

            my ( $target, $set, $source, $condition ) = $upd =~/update\s+(\w*\.*\w+)\s+(SET\s+.*?(?:\=|\|)\s*\w*\.*\w+\s+)FROM\s+(\w+\s*\w+\s*\,.*?)where(.*?)\;/gis;
            my $orig_cond = $condition;
            my @aliases   = $source =~ /\w+\s+(\w+)/gis;

            #$MR->log_err($condition);
            my @target_conditions = $condition =~ /\Q$target\E\.\w+/gis;
            @target_conditions = uniq(@target_conditions);
            $source            = $target . ",\n" . $source;

            $MR->log_err( Dumper(@target_conditions) );

         
            my @conditions_to_move  = ();
            my @conditions_to_move2 = ();
            for my $al (@aliases) {
                my @cond_to_move = $condition =~ /\Q$al\E\.\w+/gis;
                for my $c (@cond_to_move) {
                    push( @conditions_to_move, $c );
                }
                my @cond_to_move2 = $set =~ /\Q$al\E\.\w+/gis;
                for my $c (@cond_to_move2) {
                    push( @conditions_to_move, $c );
                }

            }
            my @cond_to_move3 = "$set" =~ /\=\s*(\w+\b)(?!\.)(?!\()/gis;
            for my $c (@cond_to_move3) {
                push( @conditions_to_move2, $c );
            }
            my @cond_to_move3 = "$set" =~ /\|\s*(\w+\b)(?!\.)(?!\()/gis;
            for my $c (@cond_to_move3) {
                push( @conditions_to_move2, $c );
            }


            my $conds2 = join( "\n", uniq(@conditions_to_move2) );
            my $conds  = join( "\n", uniq(@conditions_to_move) );
            my @columns  = $conds =~ /\w+\.\w+/gis;
            my @columns2 = $conds2 =~ /\w+/gis;
            my $sl_col   = join( "\,\n", @columns );
            my $sl_col2  = join( "\,\n", @columns2 );
            $sl_col =~ s/(\w+)\.(\w+)/$1.$2 $1_$2/gis;
            $sl_col2 =~ s/(\w+)\.(\w+)/$1.$2 $1_$2/gis;

            #$sl_col =~ s/(\w+)\.(\w+)/$1.$2 $1_$2/gis;
            my $target_columns = join( "\,\n", uniq(@target_conditions) );
            $target_columns =~ s/(\w+)\.(\w+)/$1.$2 $1_$2/gis;
            my $where = '';
            if ( $sl_col2 eq '' ) {
                $where =
                    "( SELECT DISTINCT\n"
                  . $target_columns . ",\n"
                  . $sl_col
                  . "\nFROM "
                  . $source
                  . " where\n"
                  . $condition
                  . ") source";
            }
            else {
                $where =
                    "( SELECT DISTINCT\n"
                  . $target_columns . ",\n"
                  . $sl_col . "\n,"
                  . $sl_col2
                  . "\nFROM "
                  . $source
                  . " where \n"
                  . $condition
                  . ") source";
            }

            # for my $al (@aliases)
            # {
            # 	 $condition =~ s/(\Q$al\E)\.(\w+)/source.$1_$2/gis;
            # 	 $set =~ s/(\Q$al\E)\.(\w+)/source.$1_$2/gis;
            # }
            my $on = '';
            for my $tcon (@target_conditions) {
                my ($src_con) = $tcon =~ /\Q$target\E\.(\w+)/gis;

                #$on = $on."\nsource".$src_con." = ".$tcon." AND ";
                $on =
                    $on
                  . "\nsource."
                  . $target . "_"
                  . $src_con . " = "
                  . $tcon . " AND ";

            }
            $on = $on . ";";
            $on =~ s/and\s+\;//gis;

            # my $on = join("\,",uniq( @target_conditions));
            $set =~ s/(\w+)\.(\w+)/$1_$2/gis;
            my $final_sql =
                "MERGE INTO "
              . $target
              . "\n USING \n"
              . $where
              . " ON \n"
              . $on
              . "\nWHEN MATCHED THEN UPDATE \n"
              . $set . ";";

            #$MR->log_err(Dumper($final_sql));
            # my @final_sql_ar = split(/\n/, $final_sql);

            $final_sql = $sql_parser->convert_sql_fragment($final_sql);

            return $final_sql;
        }
    }
    my @updates2 = $str_content =~  /update\s+\w*\.*\w+\s+\w*\s*SET\s+.*\bfrom\b\s+\w+\s*\,.*?where.*?\;/gis;
    if ( scalar @updates2 != 0 ) {

        for my $upd (@updates2) {

            my ( $target, $set, $source, $condition ) = $upd =~/update\s+(\w*\.*\w+)\s+(SET\s+.*)\bfrom(\b\s+\w+\b\s*\,.*?)where(.*?)\;/gis;
            my ($first_source) = $upd =~ /\bfrom\s+(\w+\b)/i;


            my $orig_cond = $condition;
            my @aliases   = $source =~ /\w+\s+(\w+)/gis;

            #$MR->log_err($condition);
            my @target_conditions = $condition =~ /\Q$target\E\.\w+/gis;
            @target_conditions = uniq(@target_conditions);
            $source            = $target . ",\n" . $source;
            $MR->log_err($condition);

            #my @cartesian=();
            # foreach my $a (@aliases)
            # {
            #    foreach my $b (@aliases)
            # 	{
            # 			push @cartesian, [$a, $b];
            #    }
            # }
            my @conditions_to_move  = ();
            my @conditions_to_move2 = ();
            for my $al (@aliases) {
                my @cond_to_move = $condition =~ /\Q$al\E\.\w+/gis;
                for my $c (@cond_to_move) {
                    push( @conditions_to_move, $c );
                }
                my @cond_to_move2 = $set =~ /\Q$al\E\.\w+/gis;
                for my $c (@cond_to_move2) {
                    push( @conditions_to_move, $c );
                }

            }
            my @cond_to_move3 = "$set" =~ /\=\s*(\w+\b)(?!\.)(?!\()/gis;
            for my $c (@cond_to_move3) {
                push( @conditions_to_move2, $c );
            }

            my @cond_to_move5 =
              "$set" =~ /(?:\=|\<|\>|\*|\/|\!)\s*(\w+)\s*(?!\.|())/gis;

            for my $c (@cond_to_move5) {
                push( @conditions_to_move2, $c );
            }
            my @cond_to_move6 = "$set" =~ /(\w+\.\w+)/gis;

            for my $c (@cond_to_move6) {
                push( @conditions_to_move2, $c );
            }


            my $conds2 = join( "\n", uniq(@conditions_to_move2) );

            my $conds = join( "\n", uniq(@conditions_to_move) );

            #$conds  =~ s/(?<!\.)(\b\w+\b)(?!\.)/\Q$first_source\E.$1/gis;
            #$conds2  =~ s/(?<!\.)(\b\w+\b)(?!\.)/\Q$first_source\E.$1/gis;
            my @columns  = $conds =~ /\w+\.\w+/gis;
            my @columns2 = $conds2 =~ /\w+\.*\w*/gis;

            my $sl_col  = join( "\,\n", @columns );
            my $sl_col2 = join( "\,\n", @columns2 );
            $sl_col =~ s/(\w+)\.(\w+)/$1.$2 $1_$2/gis;
            $sl_col2 =~ s/(\w+)\.(\w+)/$1.$2 $1_$2/gis;
            my $target_columns = join( "\,\n", uniq(@target_conditions) );

            $target_columns =~ s/(\w+)\.(\w+)/$1.$2 $1_$2/gis;
            my $where = '';
            if ( $sl_col2 eq '' ) {
                $where =
                    "( SELECT DISTINCT\n"
                  . $target_columns . ",\n"
                  . $sl_col
                  . "\nFROM "
                  . $source
                  . " where\n"
                  . $condition
                  . ") source";
            }
            else {
                $where =
                    "( SELECT DISTINCT\n"
                  . $target_columns . ",\n"
                  . $sl_col . ",\n"
                  . $sl_col2
                  . "\nFROM "
                  . $source
                  . " where \n"
                  . $condition
                  . ") source";
            }

            # for my $al (@aliases)
            # {
            # 	 $condition =~ s/(\Q$al\E)\.(\w+)/source.$1_$2/gis;
            # 	 $set =~ s/(\Q$al\E)\.(\w+)/source.$1_$2/gis;
            # }
            my $on = '';
            for my $tcon (@target_conditions) {
                my ($src_con) = $tcon =~ /\Q$target\E\.(\w+)/gis;
                $on =
                    $on
                  . "\nsource."
                  . $target . "_"
                  . $src_con . " = "
                  . $tcon . " AND ";

            }
            $on = $on . ";";
            $on =~ s/and\s+\;//gis;


            $set =~ s/(\w+)\.(\w+)/$1_$2/gis;

            my $final_sql =
                "MERGE INTO "
              . $target
              . "\n USING \n"
              . $where
              . " ON \n"
              . $on
              . "\nWHEN MATCHED THEN UPDATE \n"
              . $set . ";";

            #$MR->log_err(Dumper($final_sql));
            # my @final_sql_ar = split(/\n/, $final_sql);

            $final_sql = $sql_parser->convert_sql_fragment($final_sql);

            return $final_sql;
        }
    }

    my @updates3 = $str_content =~/update\s+\w*\.*\w+\s+\w*\s*SET\s+.*\bfrom\b\s*\(select\s+.*?where.*?\;/gis;
    if ( scalar @updates3 != 0 ) {

        for my $upd (@updates3) {

            my ( $target, $set, $source, $condition ) = $upd =~/update\s+(\w*\.*\w+)\s+(SET\s+.*)\bfrom\b\s*(\(select\s+.*?)where(.*?)\;/gis;
            my $orig_cond = $condition;
            my ($first_source) = $upd =~ /\)\s*(\b\w+\b)\s*\,/im;


            my @aliases = $source =~ /\w+\s+(\w+)/gis;

            #$MR->log_err($condition);
            my @target_conditions = $condition =~ /\Q$target\E\.\w+/gis;
            @target_conditions = uniq(@target_conditions);
            $source            = $target . ",\n" . $source;
            $MR->log_err($source);

            my @conditions_to_move  = ();
            my @conditions_to_move2 = ();
            for my $al (@aliases) {
                my @cond_to_move = $condition =~ /\Q$al\E\.\w+/gis;
                for my $c (@cond_to_move) {
                    push( @conditions_to_move, $c );
                }
                my @cond_to_move2 = $set =~ /\Q$al\E\.\w+/gis;
                for my $c (@cond_to_move2) {
                    push( @conditions_to_move, $c );
                }

            }
            my @cond_to_move3 = "$set" =~ /\=\s*(\w+\b)(?!\.)(?!\()/gis;
            for my $c (@cond_to_move3) {
                push( @conditions_to_move2, $c );
            }


            my @cond_to_move5 = "$set" =~ /(?:\=|\<|\>|\*|\/|\!)\s*(\w+)\s*(?!\.|())/gis;

            for my $c (@cond_to_move5) {
                push( @conditions_to_move2, $c );
            }
            my @cond_to_move6 = "$set" =~ /(\w+\.\w+)/gis;

            for my $c (@cond_to_move6) {
                push( @conditions_to_move2, $c );
            }

            my $conds2 = join( "\n", uniq(@conditions_to_move2) );

            my $conds = join( "\n", uniq(@conditions_to_move) );
            $conds =~ s/(?<!\.)(\b\w+\b)(?!\.)/\Q$first_source\E.$1/gis;
            $conds2 =~ s/(?<!\.)(\b\w+\b)(?!\.)/\Q$first_source\E.$1/gis;
            my @columns = $conds =~ /\w+\.\w+/gis;
            my @columns2 =
              $conds2 =~ /\w+\.*\w*/gis;    #$MR->log_err(Dumper(@columns2));
            my $sl_col  = join( "\,\n", @columns );
            my $sl_col2 = join( "\,\n", @columns2 );
            $sl_col =~ s/(\w+)\.(\w+)/$1.$2 $1_$2/gis;
            $sl_col2 =~ s/(\w+)\.(\w+)/$1.$2 $1_$2/gis;
            my $target_columns = join( "\,\n", uniq(@target_conditions) );

            $target_columns =~ s/(\w+)\.(\w+)/$1.$2 $1_$2/gis;
            $MR->log_err($target_columns);
            $MR->log_err($sl_col2);
            my $where = '';
            if ( $sl_col2 eq '' ) {
                $where =
                    "( SELECT DISTINCT\n"
                  . $target_columns . ",\n"
                  . $sl_col
                  . "\nFROM "
                  . $source
                  . " where\n"
                  . $condition
                  . ") source";
            }
            else {
                $where =
                    "( SELECT DISTINCT\n"
                  . $target_columns . ",\n"
                  . $sl_col . "\n"
                  . $sl_col2
                  . "\nFROM "
                  . $source
                  . " where \n"
                  . $condition
                  . ") source";
            }

            # for my $al (@aliases)
            # {
            # 	 $condition =~ s/(\Q$al\E)\.(\w+)/source.$1_$2/gis;
            # 	 $set =~ s/(\Q$al\E)\.(\w+)/source.$1_$2/gis;
            # }
            my $on = '';
            for my $tcon (@target_conditions) {
                my ($src_con) = $tcon =~ /\Q$target\E\.(\w+)/gis;

                #$on = $on."\nsource".$src_con." = ".$tcon." AND ";
                $on =
                    $on
                  . "\nsource."
                  . $target . "_"
                  . $src_con . " = "
                  . $tcon . " AND ";

            }
            $on = $on . ";";
            $on =~ s/and\s+\;//gis;


            $set =~ s/(\w+)\.(\w+)/$1_$2/gis;
            my $final_sql =
                "MERGE INTO "
              . $target
              . "\n USING \n"
              . $where
              . " ON \n"
              . $on
              . "\nWHEN MATCHED THEN UPDATE \n"
              . $set . ";";

            # my @final_sql_ar = split(/\n/, $final_sql);

            $final_sql = $sql_parser->convert_sql_fragment($final_sql);

            return $final_sql;
        }
    }
    else {

        #$str_content = $sql_parser->convert_sql_fragment($str_content);
        return $str_content;    #$MR->log_err(Dumper($str_content));
    }

}

sub uniq 
{
  my %seen;
  return grep { !$seen{$_}++ } @_;
}
