from django.test import TestCase, Client
from django.urls import reverse
from django.conf import settings



class TransactionTest(TestCase):
    fixtures = [
       "sample.json",
    ]
    def setUp(self):
        self.client = Client()
        self.url = reverse("coinapp:home")
    
    def test_login_and_make_transaction(self):
        response = self.client.get(self.url, follow=True) 
        self.assertInHTML('<h2>Log in</h2>', response.content.decode())

        # login as sulaiman and make a seller transaction of 10$ -> nusra(8921513696)
        self.client.post(reverse('login'), {'username':'8547622462', 'password':'sumee1910'}, follow=True)
        response = self.client.post(self.url, {"buyer": "8921513696","amount": "10", "description":"caring"})  

        response = self.client.get(self.url) 
        # check sulaiman has 10$ balance
        self.assertInHTML('<h3 class="text-muted">Balance: 10$</h3>', response.content.decode())
        
        # login as nusra. check she has -10$ balance
        response = self.client.post(reverse('login'), {'username':'8921513696', 'password':'sumee1910'}, follow=True)
        self.assertInHTML('<h3 class="text-muted">Balance: -10$</h3>', response.content.decode())
        
        
    def test_max_transaction(self):
        # settings.MAXIMUM_BALANCE exceeded then 400
        pass



class ListingTest(TestCase):
    fixtures = [
       "sample.json",
    ]
    def setUp(self):
        self.client = Client()
        self.url = reverse("coinapp:user_detail",kwargs={'exchange':'KKDE','user':1})
    
    def test_offerings_list(self):
        response = self.client.get(self.url) 
        rice_offering = '''
        <li class="list-group-item d-flex justify-content-between align-items-start">
            <div class="ms-2 me-auto">
                <div class="fw-bold">#1:rice</div>
                Category: Food<br>
                Matta rice<br>                
            </div>
            <h5><span class="badge text-bg-secondary">50$ per kg</span></h5>
        </li>
        '''

        self.assertInHTML(rice_offering, response.content.decode())

    def test_offering_create(self):
        self.client.post(reverse('login'), {'username':'7356775981', 'password':'sumee1910'}, follow=True)
        response = self.client.get(self.url) 
        self.assertInHTML('Add new offering', response.content.decode())

        # create a new offering
        response = self.client.post(self.url, {'action':'add', 'listing_type':'O','category':1,'heading':'test heading','detail':'test detail','rate':'test rate'}, follow=True)
        self.assertIn('Listing activated: test heading', str(list(response.context['messages'])[0]))
        self.assertEqual('O', response.context['userlistings'].filter(heading='test heading').first().listing_type)
        response = self.client.get(self.url) 
        self.assertInHTML('Add new offering', response.content.decode())        
        self.assertIn('test heading', response.content.decode())
    

    def test_want_create(self):
        self.client.post(reverse('login'), {'username':'7356775981', 'password':'sumee1910'}, follow=True)
        response = self.client.get(self.url) 
        self.assertInHTML('Add new want', response.content.decode())

        # create a new offering
        response = self.client.post(self.url, {'action':'add', 'listing_type':'W','category':1,'heading':'test heading want','detail':'test detail'}, follow=True)
        self.assertIn('Listing activated: test heading want', str(list(response.context['messages'])[0]))
        self.assertEqual('W', response.context['userlistings'].filter(heading='test heading want').first().listing_type)
        response = self.client.get(self.url)     
        div_part = '''
        <p class="lead">Wants</p>
        <ol class="list-group list-group-numbered">  
            <li class="list-group-item d-flex justify-content-between align-items-start">
                <div class="ms-2 me-auto">
                    <div class="fw-bold">#16:test heading want</div>
                    Category: Food<br>
                    test detail<br>                    
                    
        '''
        self.assertIn('test heading want', response.content.decode())