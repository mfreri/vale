#!/usr/bin/env python3
# -*- coding: utf-8 -*-
# Requires: KivyMD v0.104.1
#			PyGame v1.9.4.post1

'''
	Valentino is a game where you have to click on an avatar that changes
	position over time.

    Copyright (C) 2020 Marcelo Freri
    
    This program is free software: you can redistribute it and/or modify
    it under the terms of the GNU General Public License as published by
    the Free Software Foundation, either version 3 of the License, or
    (at your option) any later version.

    This program is distributed in the hope that it will be useful,
    but WITHOUT ANY WARRANTY; without even the implied warranty of
    MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE. See the
    GNU General Public License for more details.

    You should have received a copy of the GNU General Public License
    along with this program. If not, see <https://www.gnu.org/licenses/>.
    
    Contact author:
    mfreri@protonmail.com
'''

import sys
from kivymd.app import MDApp
from kivymd.uix.boxlayout import MDBoxLayout
from kivymd.uix.label import MDLabel
from kivymd.uix.floatlayout import MDFloatLayout
from kivymd.uix.button import MDFlatButton
from kivy.uix.button import Button
import threading
import time
import random
random.seed()


# Sets the version of the game release
_VERSION = "(beta2)"
# Sets the time of the gameplay in seconds
_PLAYTIME = 10
# Sets the debuggin messages on or off
_DEBUG = False


class Game(MDBoxLayout):
	score = 0
	highscore = 0
	time = 0
	# Used as a flag by the countdown thread
	ingame = False
	# Sets the difficulty of the game
	hard = False

	def __init__(self, **kwargs):
		super(Game, self).__init__(**kwargs)
		self.highscore = read_highscore()
		self.orientation = "vertical"
		self.padding = 10

		# Topbar
		topbar = MDBoxLayout()
		self.score_lbl = MDLabel(text="Puntaje: {} / Record: {}".format(str(self.score), str(self.highscore)))
		title = MDLabel(text="VALENTINO")
		title.theme_text_color = 'Custom'
		title.text_color = (0.84, 0.64, 0.07, 1) # orange
		title.halign = 'center'
		self.timer_lbl = MDLabel(text="Tiempo: {}s".format(self.time))
		self.timer_lbl.halign = 'right'
		topbar.add_widget(self.score_lbl)
		topbar.add_widget(title)
		topbar.add_widget(self.timer_lbl)
		topbar.size_hint = (1, 0.05)

		# Playground
		playground = MDFloatLayout()
		playground.pos_hint = {'center_x': .5, 'center_y': .5}

		# Avatar
		self.avatar = Button(background_normal = 'res/avatar1.png',
							background_down = 'res/avatar2.png',
							size_hint = (None, None),
							size = (95, 128),
							disabled = True,
							opacity = 0,
							on_press = self.touch)
		self.avatar.pos_hint = {'center_x': .5, 'center_y': .5}
		playground.add_widget(self.avatar)

		# Controls
		controls = MDFloatLayout()
		controls.size_hint = (1, .1)
		self.play_btn = MDFlatButton(text="JUGAR")
		self.play_btn.pos_hint = {'center_x': .5, 'center_y': .5}
		self.play_btn.bind(on_press=self.play)
		self.stop_btn = MDFlatButton(text="PARAR")
		self.stop_btn.pos_hint = {'center_x': .5, 'center_y': .5}
		self.stop_btn.disabled = True
		self.stop_btn.opacity = 0
		self.stop_btn.bind(on_press=self.stop)
		controls.add_widget(self.play_btn)
		controls.add_widget(self.stop_btn)

		# Main screen
		self.add_widget(topbar)
		self.add_widget(playground)
		self.add_widget(controls)

	def update_avatar_position(self):
		xpos = random.randint(10, 90) / 100
		ypos = random.randint(15, 85) / 100
		self.avatar.pos_hint = {'center_x': xpos, 'center_y': ypos}

	def update_scores(self):
		if self.score > self.highscore:
			self.highscore = self.score
			if _DEBUG: print("Highscore!")
		self.score_lbl.text="Puntaje: {} / Record: {}".format(str(self.score), str(self.highscore))

	def update_timer(self):
		# The time value is converted into integer
		self.timer_lbl.text = "Tiempo: {}s".format(str(int(self.time)))

	def countdown(self):
		delay = 1.0
		speedup = False
		while self.ingame:
			time.sleep(delay)
			self.time -= delay
			if self.time <= 0:
				# Sends the terminate signal to the thread
				self.ingame = False
			elif self.time < _PLAYTIME / 2 and not self.hard:
				# At half the playtime, the avatar position change every second
				self.hard = True
			if self.time <= _PLAYTIME / 4 and not speedup:
				# At a quarter of the playtime, the avatar position changes twice every second
				delay = delay / 2
				speedup = True
			self.update_timer()
			if self.hard: self.update_avatar_position()
			if _DEBUG: print(self.time)
		self.stop(instance=self.stop_btn)

	def hide_btn(self, instance):
		instance.opacity = 0
		instance.disabled = True

	def show_btn(self, instance):
		instance.opacity = 1
		instance.disabled = False

	def play(self, instance):
		self.score = 0
		self.time = _PLAYTIME
		self.hard = False
		self.update_scores()
		self.update_timer()
		self.update_avatar_position()
		self.show_btn(self.avatar)
		self.hide_btn(instance) # hide play button
		self.show_btn(self.stop_btn) # show stop button
		self.ingame = True
		counter = threading.Thread(target=self.countdown, daemon=True)
		counter.start()
		if _DEBUG: print("Playing.")

	def stop(self, instance):
		self.avatar.disabled = False
		self.avatar.opacity = 1
		self.hide_btn(self.avatar)
		self.hide_btn(instance) # hide stop button
		self.show_btn(self.play_btn) # show play button
		self.ingame = False
		if _DEBUG: print("Stoped.")
		write_highscore(self.highscore)

	def touch(self, instance):
		self.score += 1
		self.update_scores()
		self.update_avatar_position()
		if _DEBUG: print(self.avatar.pos_hint)


class MainApp(MDApp):
	title = "Valentino"
	icon = 'res/avatar1.png'

	def build(self):
		return Game()


def read_highscore():
	if _DEBUG: print("Reading highscore...")
	with open('vale.cfg', 'r') as f:
		data = f.read()
	if _DEBUG: print(data)
	return int(data.split()[-1])


def write_highscore(value):
	if _DEBUG: print("Writing highscore: {}".format(value))
	with open('vale.cfg', 'w') as f:
		f.write("Highscore = {}\n".format(value))


def check_dependencies():
	if _DEBUG: print("Checking dependencies...")
	is_ok = True
	modules = sys.modules
	if not 'pygame' in modules:
		print("* Requires PyGame v1.9.4.post1")
		is_ok = False
	if not 'kivymd' in modules:
		print("* Requires KivyMD v0.104.1")
		is_ok = False
	return is_ok


def intro(name, version):
	width = len(name + version) + 5
	line = "*" * width
	print('\n')
	print(line)
	print("*", name, version, "*")
	print(line)
	print('\n')


if __name__ == '__main__':
	if not check_dependencies():
		print("Something go wrong.")
		exit(1)
	intro("Valentino", _VERSION)
	MainApp().run()
	if _DEBUG: print("Done.")
