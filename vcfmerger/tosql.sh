#!/bin/bash

INPROJ=$1
#INPROJ=walk_out_10k

echo '.schema'         | sqlite3 $INPROJ.sqlite > $INPROJ.sqlite.schema
echo '.dump'           | sqlite3 $INPROJ.sqlite > $INPROJ.sqlite.sql
echo '.dump trees'     | sqlite3 $INPROJ.sqlite > $INPROJ.sqlite.sql.trees.sql
echo '.dump chrom'     | sqlite3 $INPROJ.sqlite > $INPROJ.sqlite.sql.chrom.sql
echo '.dump spps'      | sqlite3 $INPROJ.sqlite > $INPROJ.sqlite.sql.spps.sql
echo '.dump fastas'    | sqlite3 $INPROJ.sqlite > $INPROJ.sqlite.sql.fastas.sql
echo '.dump registers' | sqlite3 $INPROJ.sqlite > $INPROJ.sqlite.sql.registers.sql
