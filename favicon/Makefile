favicon.ico : \
favicon_xor_48.ppm favicon_and_48.pbm \
favicon_xor_32.ppm favicon_and_32.pbm \
favicon_xor_16.ppm favicon_and_16.pbm
	ppmtowinicon -output $@ -andpgms $^

favicon.png : \
favicon_and_16.pbm favicon_xor_16.ppm
	pnmtopng -alpha $^ > $@


favicon_xor_%.ppm : %.ppm invert_%.pgm black_%.ppm
	pnmcomp -alpha invert_$*.pgm black_$*.ppm $< > $@

favicon_and_%.pbm : %.pgm
	pgmtopbm -threshold -value 0.01 $< > $@

black_%.ppm :
	ppmmake "#000000" $* $* > $@

invert_%.pgm : %.pgm
	pnminvert $< > $@

clean :
	rm -f favicon*
