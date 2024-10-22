from django.db.models.signals import post_migrate
from django.dispatch import receiver
from .models import Faq


@receiver(post_migrate)
def create_initial_faqs(sender, **kwargs):
    question_and_answers = {
        "What is common service Centre scheme?": "Under the National e-Governance Plan (NeGP) formulated by the Department of Electronics and Information Technology (DEITY), Ministry of Communication and Information Technology, Government of India, the Common Services Centers (CSCs) are conceptualized as ICT enabled, front end service delivery points for delivery of Government, Social and Private Sector services in the areas of agriculture, health, education, entertainment, FMCG products, banking and financial services, utility payments, etc",
        "What Are The Services Provided by CSC?": "CSC (Common Service Centre) Center Offers Services are GST Registration, FSSAI Registration, MSME Registration, Trademark Registration, Government Registration, Flight Ticket Booking, Train Ticket Booking, Visa Assistance, Pancard Services, Passport Services, Insurance Services, Income Tax Filing, ISO Registration, BIS Registration, Barcode Registration, Recharge, and Bill Payments, Banking and Money Transfer, Digital Signature, Aadhaar Enrollment, Aadhaar Registration and Updation, Marriage Registration, Ration Card Services, Scholarship Registration, Educational Registrations, Govt Job Applications, Voter ID Card Services, Driving Licence Related Services, Vahan Related Services, eDistrict Services, UDID Card",
        "How do I find the common service Centre?": "You had better visit the home page https://cscindia.info and search the nearest Common Service Center",
        "What is VLE full form?": "VLE means Village Level Entrepreneur",
        "Is CSC Govt authorised?": "CSC is described as a special purpose vehicle (SPV) and named CSC e-Governance Services India Limited (CSC-SPV), which has been promoted by the government of India’s Ministry of Electronics and Information Technology (MeitY), is a “government company” under the provisions of the Companies Act of 2013 and other laws."
    }
    if sender.name == "faq":
        for question, answer in question_and_answers.items():
            if Faq.objects.count() < 4:
                if not Faq.objects.filter(question = question, answer = answer).exists():
                    Faq.objects.create(question = question, answer = answer)
            else:
                break