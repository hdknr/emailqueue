#!/bin/bash

PAVEMENT=../web/pavement.py
DIR=source/models
if [ ! -d $DIR ]; then
   mkdir $DIR;
fi

if [ "$1" == "" ]; then
  APPS="emailqueue emailsmtp emailses"
else
  APPS="$1"
fi

PAVER="paver -q -f $PAVEMENT do" 

for APP in $APPS; do
    $PAVER db model_doc $APP -s > $DIR/$APP.rst
    $PAVER db list_model $APP | while read model; do X=($model); touch $DIR/${X[0]}.rst; done 
    ER="$APP"_models_er.png
    $PAVER graph_models $APP -g -o $DIR/$ER
#
cat >> $DIR/$APP.rst << EOF

.. _$APP.models.er:

ER Diagram
============================

.. image:: $ER
EOF
#
done
