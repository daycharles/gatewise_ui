"""
Kivy-based UI for GateWise (home-friendly, modern look).
Provides a lightweight ScreenManager with Main, Settings, Users, Blackout, and Garage screens.
This file mirrors core persistence and garage control logic from the original PyQt UI.
"""

import os
import json
from datetime import datetime
from functools import partial

from kivy.app import App
from kivy.lang import Builder
from kivy.uix.screenmanager import ScreenManager, Screen, FadeTransition
from kivy.uix.boxlayout import BoxLayout
from kivy.uix.gridlayout import GridLayout
from kivy.uix.button import Button
from kivy.uix.label import Label
from kivy.uix.textinput import TextInput
from kivy.uix.scrollview import ScrollView
from kivy.uix.popup import Popup
from kivy.clock import Clock

from core.garage import GarageController

KV = """
<MainScreen>:
    name: 'main'
    BoxLayout:
        orientation: 'vertical'
        padding: 20
        spacing: 20
        canvas.before:
            Color:
                rgba: 0.13,0.32,0.41,1
            Rectangle:
                pos: self.pos
                size: self.size
        BoxLayout:
            size_hint_y: None
            height: '80dp'
            Label:
                text: 'Home Access Control'
                bold: True
                font_size: '24sp'
                color: 1,1,1,1
        GridLayout:
            cols: 2
            spacing: 10
            size_hint_y: None
            height: self.minimum_height
            Button:
                id: btn_users
                text: 'Users'
                size_hint_y: None
                height: '120dp'
                on_release: app.show_screen('users')
            Button:
                id: btn_garage
                text: 'Garage'
                size_hint_y: None
                height: '120dp'
                on_release: app.show_screen('garage')
            Button:
                id: btn_blackout
                text: 'Blackout'
                size_hint_y: None
                height: '120dp'
                on_release: app.show_screen('blackout')
            Button:
                id: btn_settings
                text: 'Settings'
                size_hint_y: None
                height: '120dp'
                on_release: app.show_screen('settings')

<UsersScreen>:
    name: 'users'
    BoxLayout:
        orientation: 'vertical'
        padding: 12
        spacing: 12
        BoxLayout:
            size_hint_y: None
            height: '48dp'
            Button:
                text: 'Back'
                size_hint_x: None
                width: '120dp'
                on_release: app.show_screen('main')
            Label:
                text: 'User Maintenance'
                color: 1,1,1,1
        BoxLayout:
            orientation: 'vertical'
            ScrollView:
                do_scroll_x: False
                BoxLayout:
                    id: users_container
                    orientation: 'vertical'
                    size_hint_y: None
                    height: self.minimum_height
            BoxLayout:
                size_hint_y: None
                height: '48dp'
                Button:
                    text: 'Add User'
                    on_release: app.open_add_user()
                Button:
                    text: 'Push to Doors'
                    on_release: app.push_to_doors()

<BlackoutScreen>:
    name: 'blackout'
    BoxLayout:
        orientation: 'vertical'
        padding: 12
        spacing: 12
        BoxLayout:
            size_hint_y: None
            height: '48dp'
            Button:
                text: 'Back'
                size_hint_x: None
                width: '120dp'
                on_release: app.show_screen('settings')
            Label:
                text: 'Blackout Schedule'
                color: 1,1,1,1
        ScrollView:
            BoxLayout:
                id: blackout_container
                orientation: 'vertical'
                size_hint_y: None
                height: self.minimum_height
        BoxLayout:
            size_hint_y: None
            height: '48dp'
            Button:
                text: 'Save'
                on_release: app.save_blackout()

<SettingsScreen>:
    name: 'settings'
    BoxLayout:
        orientation: 'vertical'
        padding: 12
        spacing: 12
        BoxLayout:
            size_hint_y: None
            height: '48dp'
            Button:
                text: 'Back'
                size_hint_x: None
                width: '120dp'
                on_release: app.show_screen('main')
            Label:
                text: 'Settings'
                color: 1,1,1,1
        BoxLayout:
            size_hint_y: None
            height: '48dp'
            Label:
                text: 'Admin password is stored in environment variable GATEWISE_ADMIN_PASSWORD'
                color: 1,1,1,1

<GarageScreen>:
    name: 'garage'
    BoxLayout:
        orientation: 'vertical'
        padding: 12
        spacing: 12
        BoxLayout:
            size_hint_y: None
            height: '48dp'
            Button:
                text: 'Back'
                size_hint_x: None
                width: '120dp'
                on_release: app.show_screen('main')
            Label:
                text: 'Garage Control'
                color: 1,1,1,1
        BoxLayout:
            size_hint_y: None
            height: '120dp'
            spacing: 12
            Button:
                text: 'Trigger Door'
                on_release: app.trigger_garage()
            Label:
                id: garage_state_label
                text: 'State: unknown'
                color: 1,1,1,1
        ScrollView:
            BoxLayout:
                id: garage_events
                orientation: 'vertical'
                size_hint_y: None
                height: self.minimum_height
"""


class MainScreen(Screen):
    pass


class UsersScreen(Screen):
    pass


class BlackoutScreen(Screen):
    pass


class SettingsScreen(Screen):
    pass


class GarageScreen(Screen):
    pass


class GateWiseKivyApp(App):
    def build(self):
        Builder.load_string(KV)
        self.sm = ScreenManager(transition=FadeTransition())
        self.sm.add_widget(MainScreen(name='main'))
        self.sm.add_widget(UsersScreen(name='users'))
        self.sm.add_widget(BlackoutScreen(name='blackout'))
        self.sm.add_widget(SettingsScreen(name='settings'))
        self.sm.add_widget(GarageScreen(name='garage'))

        # State
        self.users = []
        self.blackout = {}

        # Garage controller integration
        try:
            self.garage = GarageController()
        except Exception as e:
            print(f"[WARN] Garage controller unavailable: {e}")
            self.garage = None

        # Load persisted data
        Clock.schedule_once(lambda dt: self.load_users(), 0.1)
        Clock.schedule_once(lambda dt: self.load_blackout(), 0.1)
        Clock.schedule_interval(lambda dt: self.refresh_garage_state(), 2.0)

        return self.sm

    def show_screen(self, name: str):
        self.sm.current = name

    # --- Users ---
    def load_users(self):
        if os.path.exists('users.json'):
            try:
                with open('users.json', 'r') as f:
                    self.users = json.load(f)
            except Exception as e:
                print(f"[ERROR] Failed to load users.json: {e}")
        self.refresh_users_ui()

    def save_users(self):
        try:
            with open('users.json', 'w') as f:
                json.dump(self.users, f, indent=4)
            print('[INFO] Users saved')
        except Exception as e:
            print(f"[ERROR] Failed to save users.json: {e}")
        # push to doors if auto-sync - simple behavior: always push for now
        # self.push_to_doors()

    def refresh_users_ui(self):
        container = self.root.get_screen('users').ids.users_container
        container.clear_widgets()
        for u in self.users:
            row = BoxLayout(size_hint_y=None, height=40)
            row.add_widget(Label(text=f"{u['uid']} - {u['name']}", color=(1,1,1,1)))
            btn_edit = Button(text='Edit', size_hint_x=None, width=80)
            btn_edit.bind(on_release=partial(self.open_edit_user, u))
            row.add_widget(btn_edit)
            btn_del = Button(text='Delete', size_hint_x=None, width=80)
            btn_del.bind(on_release=partial(self.delete_user, u))
            row.add_widget(btn_del)
            container.add_widget(row)

    def open_add_user(self, *args):
        content = BoxLayout(orientation='vertical', spacing=8, padding=8)
        uid_in = TextInput(hint_text='UID')
        name_in = TextInput(hint_text='Name')
        admin_in = TextInput(hint_text='isAdmin (true/false)')
        content.add_widget(uid_in)
        content.add_widget(name_in)
        content.add_widget(admin_in)
        btn = Button(text='Add', size_hint_y=None, height=40)

        def do_add(_):
            uid = uid_in.text.strip()
            name = name_in.text.strip()
            is_admin = admin_in.text.strip().lower() in ('1','true','yes')
            if not uid or not name:
                return
            if any(x['uid'] == uid for x in self.users):
                return
            self.users.append({'uid': uid, 'name': name, 'isAdmin': is_admin})
            self.save_users()
            self.refresh_users_ui()
            popup.dismiss()

        btn.bind(on_release=do_add)
        content.add_widget(btn)
        popup = Popup(title='Add User', content=content, size_hint=(0.8, 0.5))
        popup.open()

    def open_edit_user(self, user, *args):
        content = BoxLayout(orientation='vertical', spacing=8, padding=8)
        name_in = TextInput(text=user['name'])
        admin_in = TextInput(text=str(user['isAdmin']))
        content.add_widget(Label(text=f"UID: {user['uid']}"))
        content.add_widget(name_in)
        content.add_widget(admin_in)
        btn = Button(text='Save', size_hint_y=None, height=40)

        def do_save(_):
            user['name'] = name_in.text.strip()
            user['isAdmin'] = admin_in.text.strip().lower() in ('1','true','yes')
            self.save_users()
            self.refresh_users_ui()
            popup.dismiss()

        btn.bind(on_release=do_save)
        content.add_widget(btn)
        popup = Popup(title='Edit User', content=content, size_hint=(0.8, 0.5))
        popup.open()

    def delete_user(self, user, *args):
        self.users = [u for u in self.users if u['uid'] != user['uid']]
        self.save_users()
        self.refresh_users_ui()

    def push_to_doors(self):
        # simple push: write a file or print; original code used sockets
        print('[INFO] push_to_doors called - implement network sync if needed')

    # --- Blackout ---
    def load_blackout(self):
        if os.path.exists('blackout.json'):
            try:
                with open('blackout.json', 'r') as f:
                    self.blackout = json.load(f)
            except Exception as e:
                print(f"[ERROR] Failed to load blackout.json: {e}")
        self.refresh_blackout_ui()

    def refresh_blackout_ui(self):
        container = self.root.get_screen('blackout').ids.blackout_container
        container.clear_widgets()
        for day, blocks in self.blackout.items():
            for b in blocks:
                row = BoxLayout(size_hint_y=None, height=40)
                row.add_widget(Label(text=f"{day}: {b['start']} - {b['end']}", color=(1,1,1,1)))
                container.add_widget(row)

    def save_blackout(self):
        try:
            with open('blackout.json', 'w') as f:
                json.dump(self.blackout, f, indent=4)
            print('[INFO] blackout saved')
        except Exception as e:
            print(f"[ERROR] Failed to save blackout.json: {e}")

    # --- Garage ---
    def refresh_garage_state(self):
        screen = self.root.get_screen('garage')
        label = screen.ids.garage_state_label
        if self.garage:
            state = self.garage.get_state() if hasattr(self.garage, 'get_state') else 'unknown'
            label.text = f"State: {state}"
            events = self.garage.get_recent_events() if hasattr(self.garage, 'get_recent_events') else []
            ev_container = screen.ids.garage_events
            ev_container.clear_widgets()
            for e in events:
                ev_container.add_widget(Label(text=e, size_hint_y=None, height=30, color=(1,1,1,1)))

    def trigger_garage(self):
        if self.garage:
            ok = self.garage.trigger('ui') if hasattr(self.garage, 'trigger') else False
            print(f"[GARAGE] Trigger result: {ok}")
        else:
            print('[GARAGE] No garage controller available')


def launch_ui():
    GateWiseKivyApp().run()

