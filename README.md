# Binding of Isaac Repentance - Bag of Crafting Calculator

I took the calculator from platinumgod.co.uk and modified it to use the XML files from the Switch version of Repentance (v1.5). Quick and dirty copy and paste cause I didn't feel like rewriting from scratch while testing.

Also wrote a command-line Python version that's much easier to read; it reads from the XML and stringtable files directly so if/when new updates come out, you can just replace the files as needed. Might also work with mods on PC if the XML files are edited appropriately.

Not sure if this works with other consoles yet.

To run the modified platinumgod calculator, run `python3 server.py` in the docs folder and then navigate to `http://localhost:8080`. You can also use whatever other method of serving the static files, such as this repo's github pages site.

To run the Python calculator, run `python3 crafting_calculator.py -h` and read the help text. Calculations for recipes is parallelized across all CPU cores..
