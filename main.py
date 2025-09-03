import kivy
from kivy.app import App
from kivy.lang import Builder
try:
    Builder.load_file("main.kv")
except:
    pass
from kivy.uix.boxlayout import BoxLayout
from kivy.uix.label import Label
from kivy.uix.textinput import TextInput
from kivy.uix.gridlayout import GridLayout
from kivy.uix.button import Button
from kivy.uix.screenmanager import ScreenManager, Screen
from kivy.clock import Clock
from kivy.utils import platform
from kivy.properties import ListProperty, ObjectProperty, StringProperty, \
        NumericProperty, BooleanProperty, AliasProperty
from kivy.uix.floatlayout import FloatLayout
from kivy.uix.togglebutton import ToggleButton
from kivy.metrics import sp
import random 
print(f"Platform detected: {platform}")

android_available = False
if platform == "android":
    try:
        from jnius import autoclass, cast
        from android.permissions import request_permissions, Permission
        android_available = True
        print("Android components loaded successfully")
    except ImportError as e:
        print(f"Android import failed: {e}")
        android_available = False

gps_available = False
try:
    from plyer import gps
    gps_available = True
    print("GPS (plyer) available")
except ImportError:
    print("GPS (plyer) not available - will use simulation")
    gps_available = False

class MainScreen(Screen):
    def __init__(self, **kwargs):
        super(MainScreen, self).__init__(**kwargs)
        layout = BoxLayout(orientation='vertical', spacing=20, padding=20)
        
        platform_info = f"Running on: {platform}"
        if platform == "android":
            platform_info += f" (Android features: {'✅' if android_available else '❌'})"
        else:
            platform_info += " (Desktop mode)"
        
        platform_label = Label(text=platform_info, font_size='14sp', size_hint_y=None, height='40dp')
        title = Label(text='Hospital Finder', font_size='24sp', size_hint_y=None, height='60dp')
        subtitle = Label(text='Get directions immediately!', font_size='16sp', size_hint_y=None, height='40dp')
        start_btn = Button(text='Find Emergency Services', size_hint_y=None, height='60dp')
        start_btn.bind(on_press=self.go_to_services)
        
        layout.add_widget(platform_label)
        layout.add_widget(title)
        layout.add_widget(subtitle)
        layout.add_widget(start_btn)
        self.add_widget(layout)
    
    def go_to_services(self, instance):
        self.manager.current = "services"

class ServicesScreen(Screen):
    def __init__(self, **kwargs):
        super(ServicesScreen, self).__init__(**kwargs)
        layout = BoxLayout(orientation='vertical', spacing=15, padding=20)
        
        title = Label(text='Emergency Services', font_size='20sp', size_hint_y=None, height='50dp')
        subtitle = Label(text='Tap for immediate directions!', font_size='14sp', size_hint_y=None, height='30dp')
        
        back_btn = Button(text='← Back', size_hint_y=None, height='60dp')
        hospital_btn = Button(text='🏥 Get Directions to Hospitals', size_hint_y=None, height='60dp')
        police_btn = Button(text='🚔 Get Directions to Police', size_hint_y=None, height='60dp')
        fire_btn = Button(text='🚒 Get Directions to Fire Dept', size_hint_y=None, height='60dp')
        pharmacy_btn = Button(text='💊 Get Directions to Pharmacy', size_hint_y=None, height='60dp')
        
        back_btn.bind(on_press=self.go_back)
        hospital_btn.bind(on_press=self.find_hospitals)
        police_btn.bind(on_press=self.find_police)
        fire_btn.bind(on_press=self.find_fire)
        pharmacy_btn.bind(on_press=self.find_pharmacy)
        
        layout.add_widget(title)
        layout.add_widget(subtitle)
        layout.add_widget(back_btn)
        layout.add_widget(hospital_btn)
        layout.add_widget(police_btn)
        layout.add_widget(fire_btn)
        layout.add_widget(pharmacy_btn)
        
        self.add_widget(layout)
    
    def go_back(self, instance):
        self.manager.current = "main"
    
    def find_hospitals(self, instance):
        self.get_immediate_directions("hospital")
    
    def find_police(self, instance):
        self.get_immediate_directions("police station")
    
    def find_fire(self, instance):
        self.get_immediate_directions("fire station")
        
    def find_pharmacy(self, instance):
        self.get_immediate_directions("pharmacy")
    
    def show_gps(self, instance):
        self.manager.current = "gps"
    
    def get_immediate_directions(self, place_type):
        """Get directions immediately to the nearest place of specified type"""
        if platform == "android" and android_available:
            try:
                Intent = autoclass('android.content.Intent')
                Uri = autoclass('android.net.Uri')
                PythonActivity = autoclass('org.kivy.android.PythonActivity')

                
                navigation_uri = f"google.navigation:q={place_type}&mode=d"
                
                uri = Uri.parse(navigation_uri)
                intent = Intent(Intent.ACTION_VIEW, uri)
                intent.setPackage("com.google.android.apps.maps")

                current_activity = cast('android.app.Activity', PythonActivity.mActivity)
                current_activity.startActivity(intent)
                print(f"✅ Started immediate navigation to nearest {place_type}")
                
            except Exception as e:
                print(f"❌ Google Maps navigation failed: {e}")
                try:
                    directions_url = f"https://www.google.com/maps/dir/?api=1&destination={place_type.replace(' ', '+')}&travelmode=driving"
                    
                    uri = Uri.parse(directions_url)
                    intent = Intent(Intent.ACTION_VIEW, uri)
                    current_activity = cast('android.app.Activity', PythonActivity.mActivity)
                    current_activity.startActivity(intent)
                    print(f"✅ Opened browser directions to nearest {place_type}")
                except Exception as e2:
                    print(f"❌ All navigation methods failed: {e2}")
                    search_url = f"https://www.google.com/maps/search/{place_type.replace(' ', '+')}"
                    uri = Uri.parse(search_url)
                    intent = Intent(Intent.ACTION_VIEW, uri)
                    current_activity = cast('android.app.Activity', PythonActivity.mActivity)
                    current_activity.startActivity(intent)
        else:
            print(f"🗺️ IMMEDIATE DIRECTIONS SIMULATION:")
            print(f"   Would start navigation to nearest {place_type}")
            print(f"   Navigation URL: google.navigation:q={place_type}&mode=d")
            print(f"   Directions URL: https://www.google.com/maps/dir/?api=1&destination={place_type.replace(' ', '+')}")

class GPSScreen(Screen):
    def __init__(self, **kwargs):
        super(GPSScreen, self).__init__(**kwargs)
        layout = BoxLayout(orientation='vertical', spacing=15, padding=20)
        
        gps_status = "GPS Available: "
        if platform == "android":
            gps_status += f"{'✅' if gps_available else '❌'} (Real GPS)"
        else:
            gps_status += "🎯 (Simulation Mode)"
        
        title = Label(text='GPS Location', font_size='20sp', size_hint_y=None, height='50dp')
        capability_label = Label(text=gps_status, font_size='14sp', size_hint_y=None, height='30dp')
        
        self.status_label = Label(
            text='GPS Status: Ready\nClick buttons below to test GPS functionality',
            text_size=(None, None),
            halign='center'
        )
        
        back_btn = Button(text='← Back', size_hint_y=None, height='60dp')
        permission_btn = Button(text='⚙️ Request Permissions', size_hint_y=None, height='60dp')
        location_btn = Button(text='📍 Get My Location', size_hint_y=None, height='60dp')
        directions_test_btn = Button(text='🧭 Test Directions to Hospital', size_hint_y=None, height='60dp')
        
        if platform != "android":
            simulate_btn = Button(text='🎯 Simulate GPS Location', size_hint_y=None, height='60dp')
            simulate_btn.bind(on_press=self.simulate_location)
        
        back_btn.bind(on_press=self.go_back)
        location_btn.bind(on_press=self.get_location)
        permission_btn.bind(on_press=self.request_permissions)
        directions_test_btn.bind(on_press=self.test_directions)
        
        layout.add_widget(title)
        layout.add_widget(capability_label)
        layout.add_widget(self.status_label)
        layout.add_widget(back_btn)
        layout.add_widget(permission_btn)
        layout.add_widget(location_btn)
        layout.add_widget(directions_test_btn)
        
        if platform != "android":
            layout.add_widget(simulate_btn)
        
        self.add_widget(layout)
    
    def go_back(self, instance):
        self.manager.current = "services"
    
    def test_directions(self, instance):
        """Test immediate directions functionality"""
        if platform == "android" and android_available:
            try:
                Intent = autoclass('android.content.Intent')
                Uri = autoclass('android.net.Uri')
                PythonActivity = autoclass('org.kivy.android.PythonActivity')

                uri = Uri.parse("google.navigation:q=hospital&mode=d")
                intent = Intent(Intent.ACTION_VIEW, uri)
                intent.setPackage("com.google.android.apps.maps")

                current_activity = cast('android.app.Activity', PythonActivity.mActivity)
                current_activity.startActivity(intent)
                
                self.status_label.text = "✅ Started test navigation to hospital!"
                
            except Exception as e:
                self.status_label.text = f"❌ Navigation test failed: {str(e)}"
        else:
            self.status_label.text = "🎯 Would start navigation to nearest hospital (simulation)"
            print("🧭 TEST: Would open Google Maps navigation to hospital")
    
    def request_permissions(self, instance):
        if platform == "android" and android_available:
            try:
                request_permissions([
                    Permission.ACCESS_FINE_LOCATION,
                    Permission.ACCESS_COARSE_LOCATION
                ])
                self.status_label.text = "✅ GPS Permissions: Requested successfully!"
                print("✅ GPS permissions requested on Android")
            except Exception as e:
                self.status_label.text = f"❌ Permission Error: {str(e)}"
                print(f"❌ Permission error: {e}")
        else:
            self.status_label.text = "✅ GPS Permissions: Granted (Simulated)"
            print("🎯 GPS permissions simulated - granted")
    
    def get_location(self, instance):
        if platform == "android" and gps_available:
            try:
                self.status_label.text = "📡 GPS: Getting real location..."
                print("📡 Starting real GPS on Android...")
                gps.configure(on_location=self.on_location, on_status=self.on_gps_status)
                gps.start(minTime=1000, minDistance=1)
            except Exception as e:
                self.status_label.text = f"❌ GPS Error: {str(e)}"
                print(f"❌ GPS error: {e}")
        else:
            self.status_label.text = "🎯 GPS: Simulating location acquisition..."
            print("🎯 Simulating GPS location...")
            Clock.schedule_once(lambda dt: self.simulate_location(None), 2)
    
    def simulate_location(self, instance):
        lat = 42.3601 + random.uniform(-0.05, 0.05)
        lon = -71.0589 + random.uniform(-0.05, 0.05)
        print(f"🎯 Simulated GPS coordinates: {lat:.4f}, {lon:.4f}")
        self.on_location(lat=lat, lon=lon)
    
    def on_location(self, **kwargs):
        lat = kwargs.get('lat', 'Unknown')
        lon = kwargs.get('lon', 'Unknown')
        
        self.status_label.text = (
            f"📍 Location Found!\n"
            f"Latitude: {lat:.4f}\n"
            f"Longitude: {lon:.4f}\n"
            f"Status: {'Real GPS' if platform == 'android' else 'Simulated'}\n"
            f"Ready for navigation!"
        )
        
        print(f"📍 Location result: {lat:.4f}, {lon:.4f}")
        print(f"🗺️ Navigation ready from: {lat},{lon}")
        
        self.test_nearby_search(lat, lon)
    
    def test_nearby_search(self, lat, lon):
        print(f"🏥 Navigation ready to hospitals from: {lat:.4f}, {lon:.4f}")
        print(f"🚔 Navigation ready to police from: {lat:.4f}, {lon:.4f}")
        print(f"🚒 Navigation ready to fire stations from: {lat:.4f}, {lon:.4f}")
    
    def on_gps_status(self, stype, status):
        print(f"📡 GPS Status: {stype} - {status}")
        if stype == "provider-disabled":
            self.status_label.text = "❌ GPS Error: GPS is disabled on device"

class HospitalFinderApp(App):
    def build(self):
        print("🏥 Building Hospital Finder App with Immediate Directions...")
        print(f"   Platform: {platform}")
        print(f"   Android features: {android_available}")
        print(f"   GPS available: {gps_available}")
        
        sm = ScreenManager()
        sm.add_widget(MainScreen(name="main"))
        sm.add_widget(ServicesScreen(name="services"))
        sm.add_widget(GPSScreen(name="gps"))
        return sm

if __name__ == "__main__":
    print("=" * 50)
    print("🏥 HOSPITAL FINDER - IMMEDIATE DIRECTIONS")
    print("=" * 50)
    HospitalFinderApp().run()