for f in *.pdf
do
  g=${f/.pdf/}
  pdftoppm $f $g
done
