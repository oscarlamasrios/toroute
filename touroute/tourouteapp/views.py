from tourouteapp.distmod import distancia
from django.shortcuts import render
from tourouteapp.models import Place,Route
from tourouteapp.forms import SearchingForm
from django.urls import reverse
from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.forms import UserCreationForm,AuthenticationForm
from django.shortcuts import redirect, render
import json
import urllib
import urllib.parse
import requests
import pandas as pd
import numpy as np
import math
import oauth2 as oauth


#Definimos una constante para manejar la clave
#del API con mas comodidad 
CLAVE = 'AIzaSyBP7FF2JFhwI8x1rDr1BZx4P3naciXJO6g'

def validate_username(request):
  username = request.GET.get('username',None)
  data = {
    'is_taken': User.objects.filter(username__iexact=username).exists()
  }
  return JsonResponse(data)

#Webapp authentication form
def signup_view(request):

  form = UserCreationForm(request.POST)
  if form.is_valid():
    form.save()
    username = form.cleaned_data.get('username')
    raw_password = form.cleaned_data.get('password1')
    user = authenticate(username=username, password=raw_password)
    login(request, user)
    return redirect('index')
  return render(request, 'tourouteapp/signup.html',{'form': form})

#Handles logout request
def logout_view(request):
  logout(request)
  return redirect('login_view')

def login_view(request):
  loginError = ""

  #Handles access to login page
  if request.method == 'GET':
    form = AuthenticationForm()
    context={'user':request.user,'form':form,
            'loginError':loginError}

    return render(request,'tourouteapp/login.html',context)

  #Handles login fields validation
  if request.method == 'POST':
    form = AuthenticationForm(data=request.POST)
    if form.is_valid():
      user = form.get_user()
      login(request,user)
      if 'next' in request.POST:
        return redirect(request.POST.get("next"))
      else:
        return redirect('index')
    else:
      loginError = "Usuario o contraseña incorrectos."
      form = AuthenticationForm()

  context={'user':request.user,'form':form,'loginError':loginError}
  return render(request,'tourouteapp/login.html',context)


def index(request):
  #Handles access to webapp main functionallity
  if request.method == 'GET':
    form = SearchingForm()
    context={'user':request.user,'state':'to-search','form':form}
    return render(request,'tourouteapp/index.html',context)

  #Handles requests to advance on the main functionallity flow
  if request.method == 'POST':
    form = SearchingForm(request.POST)
    if form.is_valid():

      #Search parameters, introduced by the user
      start = form.cleaned_data.get("start_point")
      ranges = form.cleaned_data.get("range_in_Km")
      ranges_in_m = ranges*1000
      place = form.cleaned_data.get("kind_of_place")

      #Getting data from a selection box retrieves a number, so we translate it
      #to a Google Places valid Place type code
      places_dictionary = {'1':"museum",'2':"art_gallery"}
      google_place = places_dictionary[place]

      places_dictionary_html = {'1':"Museos",'2':"Galerias de arte"}
      google_place_html = places_dictionary_html[place]

      ##########################################
      # 1) Searching the origin point for our route
      ##########################################
      googleurlAPI1 ='https://maps.googleapis.com/maps/api/place/textsearch/json'
      parameters = {'query': start, 'key': CLAVE}
      response = requests.get(googleurlAPI1,params=parameters)
      parsed_json = json.loads(response.text)

      #If the step 1) (Search origin) retrieves any place
      if parsed_json.get('status') == "OK":
        results = parsed_json.get('results')

        #Get the location of the origin point from the results field on the json retrieved by the api
        lat = results[0].get('geometry').get('location').get('lat')
        lng = results[0].get('geometry').get('location').get('lng')
        localizacion = str(lat)+','+str(lng)

        ##########################################
        # 2) Find interesting places arround the origin point 
        ##########################################

        googleurlAPI2='https://maps.googleapis.com/maps/api/place/nearbysearch/json'
        parameters2 = {'location':localizacion, 'radius': ranges_in_m, 'type':google_place, 'key': CLAVE}
        response2 = requests.get(googleurlAPI2,params=parameters2) 
        parsed_json2 = json.loads(response2.text)

        #If the step 2) (Search places) retrieves any place
        if parsed_json2.get('status') == "OK":
          results2 = parsed_json2.get('results')         

          latitudes=[]
          longitudes=[]
          names=[]
          posicionesmapa=[]
          elements=[]

          c=0

          #We count how many places have been found
          for i in results2:
            c+=1

          #Only 10 places will be offered to the user
          if c<=10:
            for i in results2:
              names.append(i['name'])
              longitudes.append(str(i['geometry']['location']['lng']).replace(',','.'))
              latitudes.append(str(i['geometry']['location']['lat']).replace(',','.'))
          else:
            c=10
            for i in range(10):
              names.append(results2[i]['name'])
              longitudes.append(str(results2[i]['geometry']['location']['lng']).replace(',','.'))
              latitudes.append(str(results2[i]['geometry']['location']['lat']).replace(',','.'))

          #We first set the marker for the origin
          queryStaticMap = 'https://maps.googleapis.com/maps/api/staticmap?size=1200x1200&markers=color:red%7Clabel:O%7C' + localizacion
          #and then add one marker for each fond places     
          for i in range(c):
            elements.append((i,names[i],latitudes[i],longitudes[i]))
            queryStaticMap += '&markers=color:blue%7Csize:mid%7Clabel:' + str(i) + '%7C' +str(latitudes[i])+','+(longitudes[i])

          queryStaticMap +='&key=' + CLAVE  

          #the state 'to-display' shows the map with all markers and the list of places where the user can select the desired ones
          context={'user':request.user,'state':'to-display', 'latitudes':latitudes, 'longitudes':longitudes,'mapurl':queryStaticMap,'placetype': google_place_html, 'elements' : elements, 'lat_origen':lat,'lon_origen':lng}
          return render(request,'tourouteapp/index.html',context)
        #If the step 2) (Search places) does not retrieve any place
        else:
          error="No hay resultados para esa búsqueda.";
          context={'user':request.user,'state':'to-search','form':form,'error':error}
          #Back to the beginning of the process
          return render(request,'tourouteapp/index.html',context)

      #If the step 1) (Search origin) does not retrieve any place
      else:
        error="No hay resultados para esa búsqueda.";
        context={'user':request.user,'state':'to-search', 'form': form, 'place': google_place, 'ranges': ranges_in_m, 'error':error}
        #Back to the begginning of the process
        return render(request,'tourouteapp/index.html',context)
    
    error = "No ha seleccionado ningun lugar!"
    #If we can find an element with id place, it means we come from
    #the 'to-display' state, so the second step of the
    #main functionallity should start
    if "FAILS" != request.POST.get("place","FAILS"):
      elements_withd=[]
      final_elements=[]

      salida = request.POST.getlist("place","")
      origin_data_lat = request.POST.get("origin_data_lat","")
      origin_data_lon = request.POST.get("origin_data_lon","")
      
      actual_origin_lat = origin_data_lat.replace(",",".")
      actual_origin_lon = origin_data_lon.replace(",",".")
      localizacion = str(origin_data_lat)+','+str(origin_data_lon)

      num_elem=len(salida)

      final_elements.append((0,'Punto de Partida',actual_origin_lat,actual_origin_lon,0))

      queryStaticMap = 'https://maps.googleapis.com/maps/api/staticmap?size=1200x1200&markers=color:red%7Clabel:O%7Csize:mid%7C'+ localizacion
      #We build the route (shortest path):
      #Starting with the origin point, we find the next closer point using
      #the nearest neighbor algorithm (eager) with a normalized euclidean
      #distance heuristic
      #The process is repeated updating the origin point as many times as
      #places the user wants to visit
      for i in range(num_elem):
        for j in salida:
          ja = j.split('/');
          x = distancia.distancef(float(actual_origin_lon),float(actual_origin_lat),float(ja[3]),float(ja[2]))
          elements_withd.append((ja[0],ja[1],ja[2],ja[3],x))
        #we use a dataframe to select the closest point to the actual origin, using the sort_values function
        df=pd.DataFrame(elements_withd,columns=['Posicion','Nombre','Latitud','Longitud','Distancia'])
        df=df.sort_values(by=['Distancia'],ascending=True)
        first = df.head(1)
        quitamelo=int(first.index.values.astype(int)[0])
        salida.pop(quitamelo)
        final_elements.append((first.values[0][0],first.values[0][1],first.values[0][2],first.values[0][3],first.values[0][4]))
        elements_withd.clear()
        #We add the marker corresponding to that place
        queryStaticMap += '&markers=color:blue%7Csize:mid%7Clabel:' + str(first.values[0][0]) + '%7C' +str(first.values[0][2]) +','+ str(first.values[0][3])

        actual_origin_lat = first.values[0][2]
        actual_origin_lon = first.values[0][3] 
        #ordenar distancias

      waypoints=''
      first = True;
      #We calculate the polyline that represents  the exact route
      #(street by street) we have to paint on the map 
      for i in final_elements[1:][:-1]:
        #First element is the origin, so the '|' character is unnecessary
        if first:
          first = False
        else:
          waypoints +='|'

        waypoints += 'via:'+str(i[2])+','+str(i[3])


      direction_request = 'https://maps.googleapis.com/maps/api/directions/json'
      direction_parameters = {'origin': str(final_elements[0][2])+','+str(final_elements[0][3]),
                    'destination': str(final_elements[-1][2])+','+str(final_elements[-1][3]),
                    'mode': 'bicycling', #the bicycling mode has resulted to be more precise than the 'walking'
                    'waypoints': waypoints,
                    'key': CLAVE}


      response3 = requests.get(direction_request,params=direction_parameters) 
      parsed_json3 = json.loads(response3.text)
      polyline_path=""
      error=""
      #Handle response of the opperation to get the route polyline
      if parsed_json3.get('status') == "OK":
        results3 = parsed_json3.get('routes')
        polyline_path = results3[0].get('overview_polyline').get('points')
      else:
        error="Ups! Alguien no ha podido dibujar tu ruta! :("
      
      #Adding the route to the StaticMap query
      queryStaticMap += '&path=enc:' + polyline_path
      queryStaticMap +='&key=' + CLAVE


      context={'user':request.user,'state':'to-route', 'form': form, 'elements': final_elements, 'mapurl': queryStaticMap,'error':error}
      return render(request,'tourouteapp/index.html',context)
    #If the values of the searching form are not valid
    else:
      form = SearchingForm()
      context={'error':error,'state':"to-search",'form':form}
      return render(request,'tourouteapp/index.html',context)

#Gets a list of the places visited and a tweet related to it and a link related, if exists.
def tweets(request):
  salida = request.POST.getlist("place","")

  nombres=[]
  for i in salida:
    nombre=i
    tweet,link=twitter(nombre) 
    nombres.append((nombre,tweet,link))

  context={'user':request.user,'tweetlist':nombres}
  return render(request,'tourouteapp/tweets.html',context)

#Gets a list for a string (place name) given
def twitter(place):
  CONSUMER_KEY= 'JUkjEEHlhswpQjVDrXnEjuY1u'
  CONSUMER_SECRET= 'U6XVyHnxXs6305fD2QVdvzLMkex8tIXTUfl3aMITH6KMqQSVSV'
  ACCESS_KEY = "1077848364-eP8DRhkDvjlF4KJSwIz6Ku1q0b6LrRJCiXDtkLl"
  ACCESS_SECRET = "PptYCoq6ba3An8HMSPo2f76NN4rD5wl82Kzasbv0qFAX1"
  consumer = oauth.Consumer(key=CONSUMER_KEY, secret=CONSUMER_SECRET)
  access_token = oauth.Token(key=ACCESS_KEY, secret=ACCESS_SECRET)
  client = oauth.Client(consumer, access_token)
  params = {'count': '3','q':place}
  twurl = "https://api.twitter.com/1.1/search/tweets.json?"+urllib.parse.urlencode(params)
  response, data = client.request(twurl)
  statuses = json.loads(data.decode('utf-8'))
  #If there are tweets 
  if len(statuses.get('statuses'))!=0:
    #If it has any link in it
    if len(statuses.get('statuses')[0].get('entities').get('urls')) !=0 :
      link = statuses.get('statuses')[0].get('entities').get('urls')[0].get('url')
    else:
      link=""
    #The tweet returned is the first found
    tweet = statuses.get('statuses')[0].get('text')
  else:
    link=""
    tweet="Uy, no hay tweets sobre este lugar :("
  return tweet,link
