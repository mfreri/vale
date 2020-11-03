#!/usr/bin/env python3
# -*- coding: utf-8 -*-

with open('../vale.cfg', 'r') as f:
	data = f.read()
print("Highscore: {}".format(data.split()[-1]))

new_hs = int(input("Enter new highscore: "))
with open('../vale.cfg', 'w') as f:
	f.write("Highscore = {}\n".format(new_hs))
print("Value changed.")
