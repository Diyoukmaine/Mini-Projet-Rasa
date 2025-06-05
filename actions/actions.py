# This files contains your custom actions which can be used to run
# custom Python code.
#
# See this guide on how to implement these action:
# https://rasa.com/docs/rasa/custom-actions


# This is a simple example for a custom action which utters "Hello World!"


from typing import Any, Text, Dict, List
from rasa_sdk import Action, Tracker, FormValidationAction
from rasa_sdk.executor import CollectingDispatcher
from rasa_sdk.types import DomainDict
from rasa_sdk.events import SlotSet
import requests
import json
from datetime import datetime
from rasa_sdk.events import FollowupAction
from typing import List, Dict, Text
import smtplib
from email.message import EmailMessage

###############################################
from rasa_sdk import Action, Tracker
from rasa_sdk.executor import CollectingDispatcher
from rasa_sdk.events import SlotSet

class ActionHandleReservationConfirmation(Action):
    def name(self):
        return "action_handle_reservation_confirmation"

    def run(self, dispatcher, tracker, domain):
        booking_type = tracker.get_slot("booking_type")

        if booking_type == "flight":
            return [SlotSet("confirmed", True), FollowupAction("action_confirm_reservation")]
        elif booking_type == "hotel":
            return [SlotSet("confirmed", True), FollowupAction("action_confirm_reservation_hotel")]
        else:
            dispatcher.utter_message(text="Je ne sais pas ce que vous essayez de confirmer.")
            return []

#######################change option###################


class ActionHandleChangeHotelReservation(Action):
    def name(self) -> Text:
        return "action_handle_change_hotel_reservation"

    def run(self, dispatcher: CollectingDispatcher,
            tracker: Tracker,
            domain: Dict) -> List[Dict]:
        
        dispatcher.utter_message(text="✅ تم تحديث بيانات الحجز، جاري البحث عن خيارات فنادق جديدة...")
        return [FollowupAction("action_search_hotels")]

class ActionHandleChangeFlightReservation(Action):
    def name(self) -> Text:
        return "action_handle_change_flight_reservation"

    def run(self, dispatcher: CollectingDispatcher,
            tracker: Tracker,
            domain: Dict) -> List[Dict]:

        dispatcher.utter_message(text="✈️ تم تحديث تفاصيل الرحلة. جاري جلب الخيارات الجديدة...")
        return [FollowupAction("action_search_flights")]



############# Hotel  actions start  ###########


class HotelBookingForm(FormValidationAction):
    def name(self) -> Text:
        return "validate_hotel_booking_form"

    def validate_ville_hotel(
        self,
        slot_value: Any,
        dispatcher: CollectingDispatcher,
        tracker: Tracker,
        domain: DomainDict,
    ) -> Dict[Text, Any]:
        if slot_value and len(slot_value) > 2:
            return {"ville_hotel": slot_value}
        else:
            dispatcher.utter_message(text="من فضلك أدخل المدينة التي تريد الحجز فيها بشكل صحيح.")
            return {"ville_hotel": None}

    def validate_categorie_hotel(
        self,
        slot_value: Any,
        dispatcher: CollectingDispatcher,
        tracker: Tracker,
        domain: DomainDict,
    ) -> Dict[Text, Any]:
        valid_categories = ["3", "4", "5", "3 نجوم", "4 نجوم", "5 نجوم"]
        if any(str(cat) in slot_value for cat in valid_categories):
            return {"categorie_hotel": slot_value}
        else:
            dispatcher.utter_message(text="يرجى تحديد عدد النجوم (مثلاً: 4 نجوم).")
            return {"categorie_hotel": None}

    def validate_quartier(
        self,
        slot_value: Any,
        dispatcher: CollectingDispatcher,
        tracker: Tracker,
        domain: DomainDict,
    ) -> Dict[Text, Any]:
        if slot_value and len(slot_value) > 2:
            return {"quartier": slot_value}
        else:
            dispatcher.utter_message(text="يرجى إدخال اسم الحي المطلوب بشكل صحيح.")
            return {"quartier": None}

    def validate_nombre_personnes(
        self,
        slot_value: Any,
        dispatcher: CollectingDispatcher,
        tracker: Tracker,
        domain: DomainDict,
    ) -> Dict[Text, Any]:
        try:
            number = int("".join(filter(str.isdigit, slot_value)))
            if number > 0:
                return {"nombre_personnes": slot_value}
            else:
                dispatcher.utter_message(text="يرجى إدخال عدد صحيح للأشخاص.")
                return {"nombre_personnes": None}
        except:
            dispatcher.utter_message(text="كم عدد الأشخاص؟ (مثلاً: شخصين)")
            return {"nombre_personnes": None}

class ActionSearchHotels(Action):
    def name(self) -> Text:
        return "action_search_hotels"

    def run(self, dispatcher: CollectingDispatcher,
            tracker: Tracker,
            domain: Dict[Text, Any]) -> List[Dict[Text, Any]]:
        
        ville_hotel = tracker.get_slot("ville_hotel")

        # hotels = [
        #     {
        #         "nom": "فندق الأطلس الكبير",
        #         "categorie_hotel": "5",
        #         "prix": "800 درهم/ليلة",
        #         "quartier": "وسط المدينة",
        #         "amenities": "مسبح، سبا، واي فاي مجاني"
        #     },
        #     {
        #         "nom": "فندق المحيط الأزرق",
        #         "categorie_hotel": "4", 
        #         "prix": "600 درهم/ليلة",
        #         "quartier": "قرب الشاطئ",
        #         "amenities": "إطلالة على البحر، مطعم، موقف سيارات"
        #     },
        #     {
        #         "nom": "فندق الرياض التقليدي",
        #         "categorie_hotel": "3",
        #         "prix": "400 درهم/ليلة", 
        #         "quartier": "المدينة القديمة",
        #         "amenities": "تصميم تقليدي، فطار مجاني، تكييف"
        #     }
        # ]
        
        hotels = [
            {
                "nom": "فندق النخيل الفاخر",
                "categorie_hotel": "5",
                "prix": "1200 درهم/ليلة",
                "quartier": "حي النخيل",
                "amenities": "مسبح، سبا، واي فاي مجاني، خدمة الغرف"
            },
            {
                "nom": "رياض الأندلس",
                "categorie_hotel": "4",
                "prix": "850 درهم/ليلة",
                "quartier": "المدينة القديمة",
                "amenities": "فطور مغربي، تراس بإطلالة، تكييف"
            },
            {
                "nom": "فندق مراكش بلازا",
                "categorie_hotel": "4",
                "prix": "700 درهم/ليلة",
                "quartier": "جيليز",
                "amenities": "موقف سيارات، مطعم، خدمة نقل إلى المطار"
            },
            {
                "nom": "رياض الوردة البيضاء",
                "categorie_hotel": "3",
                "prix": "450 درهم/ليلة",
                "quartier": "باب دكالة",
                "amenities": "تصميم تقليدي، فطور مجاني، حديقة داخلية"
            },
            {
                "nom": "فندق زهراء",
                "categorie_hotel": "2",
                "prix": "300 درهم/ليلة",
                "quartier": "حي السلام",
                "amenities": "واي فاي، مكيف، استقبال 24/24"
            }
        ]

        message = f"إليك خيارات الفنادق في {ville_hotel}:\n\n"
        for i, hotel in enumerate(hotels, 1):
            message += f"{i}. 🏨 {hotel['nom']}\n"
            message += f"   ⭐ التصنيف: {hotel['categorie_hotel']} نجوم\n"
            message += f"   💰 السعر: {hotel['prix']}\n"
            message += f"   📍 الموقع: {hotel['quartier']}\n"
            message += f"   🎯 المرافق: {hotel['amenities']}\n\n"

        message += "أي فندق تفضل؟ اكتب رقم الخيار المطلوب."
        
        dispatcher.utter_message(text=message)

        return [
            SlotSet("booking_type", "hotel"),
            SlotSet("available_hotels", json.dumps(hotels))
            #SlotSet("available_hotels", json.dumps(hotels))  # 🔒 store hotels as JSON
        ]

class ActionAskConfirmReservationHotel(Action):
    def name(self) -> Text:
        return "action_ask_confirm_reservation_hotel"

    def run(self, dispatcher: CollectingDispatcher,
            tracker: Tracker,
            domain: Dict[Text, Any]) -> List[Dict[Text, Any]]:

        hotel_summary = tracker.get_slot("hotel_summary")
        if hotel_summary:
            dispatcher.utter_message(text=hotel_summary)
        else:
            dispatcher.utter_message(text="هل ترغب في تأكيد الحجز؟")

        return []

class ActionConfirmReservationHotel(Action):
    def name(self) -> Text:
        return "action_confirm_reservation_hotel"

    def run(self, dispatcher: CollectingDispatcher,
            tracker: Tracker,
            domain: Dict[Text, Any]) -> List[Dict[Text, Any]]:

        hotel_summary = tracker.get_slot("hotel_summary")
        ville_hotel = tracker.get_slot("ville_hotel")
        categorie_hotel = tracker.get_slot("categorie_hotel")
        quartier = tracker.get_slot("quartier")
        nombre_personnes = tracker.get_slot("nombre_personnes")
        
        confirmation_message = "✅ تم تأكيد حجزك بنجاح!\n\n"
        
        confirmation_message += "📋 تفاصيل حجز الفندق:\n"
        confirmation_message += f"🏨 المدينة: {ville_hotel}\n"
        confirmation_message += f"⭐️ الفئة: {categorie_hotel}\n"
        confirmation_message += f"📍 الحي: {quartier}\n"
        confirmation_message += f"👥 عدد الأشخاص: {nombre_personnes}\n\n"

        # if hotel_summary:
        #     # Supprimer la question si elle est incluse dans le résumé
        #     cleaned_summary = hotel_summary.replace("هل ترغب في تأكيد الحجز؟", "").strip()
        #     confirmation_message += f"{cleaned_summary}\n\n"
        # else :    
        #     confirmation_message = "📋 تفاصيل حجز الفندق:\n"
        #     confirmation_message += f"🏨 المدينة: {ville_hotel}\n"
        #     confirmation_message += f"⭐️ الفئة: {categorie_hotel}\n"
        #     confirmation_message += f"📍 الحي: {quartier}\n"
        #     confirmation_message += f"👥 عدد الأشخاص: {nombre_personnes}\n"


        #confirmation_message += "📧 ستصلك رسالة تأكيد على بريدك الإلكتروني.\n"
        confirmation_message += "🏨 نتمنى لك إقامة ممتعة وراحة تامة!"

        dispatcher.utter_message(text=confirmation_message)

        return [
            SlotSet("booking_type", None),
            SlotSet("ville_hotel", None),
            SlotSet("categorie_hotel", None),
            SlotSet("quartier", None),
            SlotSet("nombre_personnes", None),
            SlotSet("selected_option", None),
            SlotSet("ville_depart", None),
            SlotSet("ville_destination", None),
            SlotSet("date_depart", None),
            SlotSet("date_retour", None),
            SlotSet("type_vol", None),
            SlotSet("classe", None),
        ]

class ActionHandleHotelSelection(Action):
    def name(self) -> Text:
        return "action_handle_hotel_selection"

    def run(self, dispatcher: CollectingDispatcher,
            tracker: Tracker,
            domain: Dict[Text, Any]) -> List[Dict[Text, Any]]:

        import json

        user_input = tracker.latest_message.get('text')

        try:
            selected_index = int(user_input.strip()) - 1
        except ValueError:
            dispatcher.utter_message(text="يرجى إدخال رقم صالح للاختيار.")
            return []

        hotels_data = tracker.get_slot("available_hotels")
        if not hotels_data:
            dispatcher.utter_message(text="⚠ لم أتمكن من العثور على خيارات الفنادق. حاول البحث مرة أخرى.")
            return []

        hotels = json.loads(hotels_data)

        if 0 <= selected_index < len(hotels):
            hotel = hotels[selected_index]

            summary = (
                f"🏨 لقد اخترت:\n"
                f"📌 الاسم: {hotel['nom']}\n"
                f"⭐ التصنيف: {hotel['categorie_hotel']} نجوم\n"
                f"📍 الموقع: {hotel['quartier']}\n"
                f"💵 السعر: {hotel['prix']}\n"
                f"🎯 المرافق: {hotel['amenities']}\n\n"
                f"هل ترغب في تأكيد الحجز؟"
            )

            dispatcher.utter_message(text=summary)

            return [
                SlotSet("selected_option", user_input),
                SlotSet("selected_hotel", hotel),
                SlotSet("hotel_summary", summary),
                SlotSet("requested_slot", None)
            ]
        else:
            dispatcher.utter_message(text="الرقم الذي أدخلته غير موجود. يرجى المحاولة برقم آخر.")
            return []

#################Hotel  actions end################

############# flight  actions start  ###########

    
class FlightBookingForm(FormValidationAction):
    def name(self) -> Text:
        return "validate_flight_booking_form"

    def validate_ville_depart(
        self,
        slot_value: Any,
        dispatcher: CollectingDispatcher,
        tracker: Tracker,
        domain: DomainDict,
    ) -> Dict[Text, Any]:
        """Valider la ville de départ."""
        if slot_value and len(slot_value) > 2:
            return {"ville_depart": slot_value}
        else:
            dispatcher.utter_message(text="من فضلك أدخل مدينة الانطلاق بشكل صحيح.")
            return {"ville_depart": None}

    def validate_ville_destination(
        self,
        slot_value: Any,
        dispatcher: CollectingDispatcher,
        tracker: Tracker,
        domain: DomainDict,
    ) -> Dict[Text, Any]:
        """Valider la ville de destination."""
        if slot_value and len(slot_value) > 2:
            ville_depart = tracker.get_slot("ville_depart")
            if ville_depart and slot_value.lower() == ville_depart.lower():
                dispatcher.utter_message(text="مدينة الوصول يجب أن تكون مختلفة عن مدينة الانطلاق.")
                return {"ville_destination": None}
            return {"ville_destination": slot_value}
        else:
            dispatcher.utter_message(text="من فضلك أدخل مدينة الوصول بشكل صحيح.")
            return {"ville_destination": None}
    
    def validate_classe(
        self,
        slot_value: Any,
        dispatcher: CollectingDispatcher,
        tracker: Tracker,
        domain: DomainDict,
    ) -> Dict[Text, Any]:
        """Valider le classe."""
        valid_types = ["الدرجة الأولى", "درجة الأعمال", "اقتصادية"]
        if slot_value and any(vtype in slot_value.lower() for vtype in [t.lower() for t in valid_types]):
            return {"classe": slot_value}
        else:
            dispatcher.utter_message(text="من فضلك اختر " \
            " درجة الرحلة: اقتصادية فقط  أو الدرجة الأولى أو درجة الأعمال  ")
            return {"classe": None}
        
    def validate_type_vol(
        self,
        slot_value: Any,
        dispatcher: CollectingDispatcher,
        tracker: Tracker,
        domain: DomainDict,
    ) -> Dict[Text, Any]:
        """Valider le type de vol."""
        valid_types = ["ذهاب فقط", "ذهاب وإياب", "aller simple", "aller retour"]
        if slot_value and any(vtype in slot_value.lower() for vtype in [t.lower() for t in valid_types]):
            return {"type_vol": slot_value}
        else:
            dispatcher.utter_message(text="من فضلك اختر نوع الرحلة: ذهاب فقط أو ذهاب وإياب")
            return {"type_vol": None}

    def validate_date_depart(
        self,
        slot_value: Any,
        dispatcher: CollectingDispatcher,
        tracker: Tracker,
        domain: DomainDict,
    ) -> Dict[Text, Any]:
        """Valider la date de départ."""
        if slot_value:
            # Ici vous pouvez ajouter une validation de format de date
            return {"date_depart": slot_value}
        else:
            dispatcher.utter_message(text="من فضلك أدخل تاريخ الانطلاق.")
            return {"date_depart": None}

    def validate_date_retour(
        self,
        slot_value: Any,
        dispatcher: CollectingDispatcher,
        tracker: Tracker,
        domain: DomainDict,
    ) -> Dict[Text, Any]:
        """Valider la date de retour."""
        type_vol = tracker.get_slot("type_vol")
        if type_vol and ("إياب" in type_vol or "retour" in type_vol.lower()):
            if slot_value:
                return {"date_retour": slot_value}
            else:
                dispatcher.utter_message(text="من فضلك أدخل تاريخ العودة للرحلة ذهاب وإياب.")
                return {"date_retour": None}
        else:
            # Pour les vols aller simple, pas besoin de date de retour
            return {"date_retour": slot_value}

class ActionAskConfirmReservationFlight(Action):
    def name(self) -> Text:
        return "action_ask_confirm_reservation"

    def run(self, dispatcher: CollectingDispatcher,
            tracker: Tracker,
            domain: Dict[Text, Any]) -> List[Dict[Text, Any]]:

        flight_summary = tracker.get_slot("flight_summary")
        if flight_summary:
            dispatcher.utter_message(text=flight_summary)
        else:
            dispatcher.utter_message(text="هل ترغب في تأكيد الحجز؟")

        return []


class ActionConfirmReservationFlight(Action):
    def name(self) -> Text:
        return "action_confirm_reservation"

    def run(self, dispatcher: CollectingDispatcher,
            tracker: Tracker,
            domain: Dict[Text, Any]) -> List[Dict[Text, Any]]:

        print("🛫 Slot flight_summary dans action_confirm_reservation:", tracker.get_slot("flight_summary"))
        print("🧑‍💻 Slot selected_flight:", tracker.get_slot("selected_flight"))

        email = tracker.get_slot("email")
        ville_depart = tracker.get_slot("ville_depart")
        ville_destination = tracker.get_slot("ville_destination")
        date_depart = tracker.get_slot("date_depart")

        # confirmation_message = (
        #     f"✅ تم تأكيد حجزك!\n"
        #     f"✈️ من {ville_depart} إلى {ville_destination}\n"
        #     f"📅 في {date_depart}\n\n"
        #     "🙏 شكراً لثقتك بنا!"
        # )
        #dispatcher.utter_message(text=confirmation_message)
        flight_summary = tracker.get_slot("flight_summary")
        #if flight_summary:
        #    dispatcher.utter_message(text=f"✅ تم تأكيد حجزك بنجاح!\n\n{flight_summary}\n\n📧 ستصلك رسالة تأكيد عبر البريد الإلكتروني.\n🎉 رحلة موفقة!")

        # إرسال بريد إلكتروني
        if email:
            try:
                msg = EmailMessage()
                # Supprimer la question à la fin si elle existe
                cleaned_summary = flight_summary.replace("هل ترغب في تأكيد الحجز؟", "").strip()
    
                msg.set_content(
                    f"✅ تم تأكيد حجزك بنجاح!\n\n{cleaned_summary}\n🎉 رحلة موفقة!"
                )
                msg["Subject"] = "تأكيد حجز الرحلة"
                msg["From"] = "diyoukmaine@gmail.com"
                msg["To"] = email

                with smtplib.SMTP_SSL("smtp.gmail.com", 465) as server:
                    server.login("diyoukmaine@gmail.com", "zosx tgyq knzb hhoj")
                    server.send_message(msg)

                dispatcher.utter_message(text="📧 تم إرسال رسالة التأكيد إلى بريدك الإلكتروني. 🎉 رحلة موفقة!")
            except Exception as e:
                import traceback
                print("SMTP Exception:", traceback.format_exc())
                print("خطأ أثناء إرسال الإيميل:", e)
                dispatcher.utter_message(text="⚠️ لم نتمكن من إرسال الإيميل حالياً.")
        else:
            dispatcher.utter_message(text="⚠️ لم يتم توفير بريد إلكتروني لإرسال التأكيد.")

        return [SlotSet(slot, None) for slot in [
            "ville_depart", "ville_destination", "date_depart", "date_retour", "type_vol", "classe", "email","ville_hotel","categorie_hotel","quartier","nombre_personnes","flight_summary","selected_option","selected_flight"
        ]]


class ActionHandleFlightSelection(Action):
    def name(self) -> Text:
        return "action_handle_flight_selection"

    def run(self, dispatcher: CollectingDispatcher,
            tracker: Tracker,
            domain: Dict[Text, Any]) -> List[Dict[Text, Any]]:

        user_input = tracker.latest_message.get('text')

        try:
            selected_index = int(user_input.strip()) - 1
        except ValueError:
            dispatcher.utter_message(text="يرجى إدخال رقم صالح للاختيار.")
            return []

        import json

        flights_data = tracker.get_slot("available_flights")
        if not flights_data:
            dispatcher.utter_message(text="⚠ لم أتمكن من العثور على نتائج الرحلات. حاول البحث مرة أخرى.")
            return []
        
        if isinstance(flights_data, str):
            flights = json.loads(flights_data)
        else:
            flights = flights_data

         #flights = json.loads(flights_data)

        # flights = [
        #     {
        #         "airline": "الخطوط الملكية المغربية",
        #         "price": "2500 درهم",
        #         "departure_time": "14:30",
        #         "arrival_time": "18:45",
        #         "duration": "4س 15د"
        #     },
        #     {
        #         "airline": "الخطوط الجوية الفرنسية",
        #         "price": "2800 درهم",
        #         "departure_time": "10:15",
        #         "arrival_time": "14:30",
        #         "duration": "4س 15د"
        #     },
        #     {
        #         "airline": "طيران الإمارات",
        #         "price": "3200 درهم",
        #         "departure_time": "22:00",
        #         "arrival_time": "08:30+1",
        #         "duration": "8س 30د"
        #     }
        # ]

        if 0 <= selected_index < len(flights):
            flight = flights[selected_index]
            #confirmation = f"🛫 لقد اخترت:\n✈️ {flight['airline']} - {flight['price']}\n🕓 {flight['departure_time']} ➡️ {flight['arrival_time']}\n⏱️ المدة: {flight['duration']}\n\nهل ترغب في تأكيد الحجز؟"
            confirmation = (
                f"🛫 لقد اخترت:\n"
                f"✈️ شركة الطيران: {flight.get('gate', 'غير معروف')} - السعر: {flight.get('price', 'غير متوفر')} درهم\n"
                f"🕓 مدة الرحلة: {flight.get('duration', 'غير متوفر')} دقيقة\n"
                f"🛬 من {flight.get('origin', 'غير معروف')} إلى {flight.get('destination', 'غير معروف')}\n"
                f"📅 تاريخ العودة: {flight.get('return_date', 'غير متوفر')}\n\n"
                "هل ترغب في تأكيد الحجز؟"
            )

            #dispatcher.utter_message(text=confirmation)
            dispatcher.utter_message(text=f"Debug: saved flight summary:\n{confirmation}")
            print("DEBUG: saved flight_summary slot:", confirmation)

            return [
                SlotSet("selected_option", user_input),
                SlotSet("selected_flight", flight),
                SlotSet("flight_summary", confirmation),
                SlotSet("requested_slot", None)
            ]
        else:
            dispatcher.utter_message(text="الرقم الذي أدخلته غير موجود. يرجى المحاولة برقم آخر.")
            return []

class ActionSearchFlights(Action):
    def name(self) -> Text:
        return "action_search_flights"

    def run(self, dispatcher: CollectingDispatcher,
            tracker: Tracker,
            domain: Dict[Text, Any]) -> List[Dict[Text, Any]]:

        # 🔁 Dictionnaire arabe -> IATA
        city_to_iata = {
            "الدار البيضاء": "CMN",
            "باريس": "PAR",
            "مراكش": "RAK",
            "الرباط": "RBA",
            "طنجة": "TNG",
            "أكادير": "AGA",
            "دبي": "DXB",
            "اسطنبول": "IST",
            "نيويورك": "NYC",
            "لندن": "LON"
        }

        # 📥 Slots
        ville_depart = tracker.get_slot("ville_depart")
        ville_destination = tracker.get_slot("ville_destination")
        date_depart = tracker.get_slot("date_depart")
        date_retour = tracker.get_slot("date_retour")
        type_vol = tracker.get_slot("type_vol")
        classe = tracker.get_slot("classe") or "économique"

        # 📌 Vérification
        if not all([ville_depart, ville_destination, date_depart, type_vol]):
            dispatcher.utter_message(text="❗معلومات الرحلة غير مكتملة. يرجى ملء جميع الحقول المطلوبة.")
            return []

        # 🔁 Conversion en IATA
        origin = city_to_iata.get(ville_depart)
        destination = city_to_iata.get(ville_destination)

        if not origin or not destination:
            dispatcher.utter_message(text="❌ لا يمكننا تحديد رمز المدينة. تأكد من إدخال مدن معروفة.")
            return []

        # try:
        #     flights = self.search_flights_api(origin, destination, date_depart, date_retour, type_vol, classe)

        #     if flights:
        #         message = f"🛫 إليك بعض الرحلات من {ville_depart} إلى {ville_destination} بتاريخ {date_depart}:\n\n"
        #         for i, flight in enumerate(flights[:5], 1):
        #             message += f"{i}. 💺 السعر: {flight['price']}$\n\n"
        #             message += f"   🧾 المزود: {flight['gate']}\n\n"
        #             message += f"   ⌚ المدة: {flight['duration']} دقيقة\n\n"
        #             message += f"   🔁 عدد التوقفات: {flight['stops']}\n\n"
        #             message += f"   📅 العودة: {flight['return_date']}\n\n"
        #             message += f"   🆔 الرمز: {flight['origin']} ➡ {flight['destination']}\n\n"

        #         message += "✈ أي خيار تفضل؟"
        #     else:
        #         message = f"عذراً، لم يتم العثور على رحلات من {ville_depart} إلى {ville_destination} في التاريخ المحدد."

        #     dispatcher.utter_message(text=message)
        # except Exception as e:
        #     print("⚠ Erreur:", e)
        #     dispatcher.utter_message(text="⚠ حدث خطأ أثناء الاتصال بخدمة الرحلات.")
        try:
            flights = self.search_flights_api(origin, destination, date_depart, date_retour, type_vol, classe)

            if flights:
                message = f"🛫 إليك بعض الرحلات من {ville_depart} إلى {ville_destination} بتاريخ {date_depart}:\n\n"
                
                for i, flight in enumerate(flights[:5], 1):
                    message += (
                        f"{i}. 💺 السعر: {flight.get('price', 'غير متوفر')}$\n"
                        f"   🧾 المزود: {flight.get('gate', 'غير متوفر')}\n"
                        f"   ⌚ المدة: {flight.get('duration', 'غير متوفرة')} دقيقة\n"
                        f"   🔁 عدد التوقفات: {flight.get('stops', 'غير متوفر')}\n"
                        f"   📅 العودة: {flight.get('return_date', 'غير متوفرة')}\n"
                        f"   🆔 الرمز: {flight.get('origin', '?')} ➡ {flight.get('destination', '?')}\n\n"
                    )

                message += "✈ يرجى إدخال رقم الخيار الذي تريده (مثلاً: 1 أو 2...)."
            else:
                message = f"عذراً، لم يتم العثور على رحلات من {ville_depart} إلى {ville_destination} في التاريخ المحدد."

            dispatcher.utter_message(text=message)

        except Exception as e:
            print(f"⚠ خطأ أثناء جلب الرحلات: {e}")
            dispatcher.utter_message(text="⚠ حدث خطأ أثناء الاتصال بخدمة الرحلات. حاول مرة أخرى لاحقاً.")


        return [SlotSet("available_flights", json.dumps(flights)),SlotSet("booking_type", "flight")]

    def search_flights_api(self, origin, destination, date_depart, return_date, trip_type, travel_class):
        try:
            
            token = "8204f952cf30b8def2b7fb27b7550b48"
                
            # Mappage de la classe de voyage en entier
            class_map = {
                "درجة اقتصادية": 0,
                "درجة رجال الاعمال": 1,
                "درجة أولى": 2
            }
            trip_class = class_map.get(travel_class.lower(), 0)

            # Détermination du type de voyage
            one_way = 'true' if trip_type == 'ذهاب' else 'false'

            url = (
                f"https://api.travelpayouts.com/v2/prices/latest"
                f"?origin={origin}&destination={destination}"
                f"&depart_date={date_depart}"
                f"&return_date={return_date or ''}"
                f"&trip_class={trip_class}"
                f"&one_way={one_way}"
                f"&currency=usd&token={token}"
            )
            # url = (
            #     f"https://api.travelpayouts.com/v2/prices/latest"
            #     f"?origin={origin}&destination={destination}"
            #     f"&depart_date={date_depart}"
            #     f"&return_date={return_date or ''}"
            #     f"&currency=usd&token={token}"
            # )

            response = requests.get(url)
            response.raise_for_status()
            data = response.json()

            flights = []

            for item in data.get("data", []):
                flights.append({
                    "origin": item.get("origin", origin),
                    "destination": item.get("destination", destination),
                    "price": item.get("value", "؟"),
                    "duration": item.get("duration", "؟"),
                    "stops": item.get("number_of_changes", "؟"),
                    "gate": item.get("gate", "؟"),
                    "return_date": item.get("return_date", "؟")
                })

            return flights
        
        except Exception as e:
            print("❌ Erreur dans l'API:", e)
            return [SlotSet("booking_type", "flight")]
