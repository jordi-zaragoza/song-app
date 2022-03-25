import requests
from bs4 import BeautifulSoup 
import pandas as pd
import numpy as np
import re
from config import *
import spotipy
import json
from spotipy.oauth2 import SpotifyClientCredentials

class Spoty_jzar():
    '''
    This is the class Spoty_jzar used to handle spotyfy API
    ''' 
    
    call_counter = 0    
    unknown_artists = 0
    

# -------------------------------

    def __init__(self):        
        print("Initialize sp")
        
        self.new_call()
        
        self.sp = spotipy.Spotify(auth_manager=SpotifyClientCredentials(client_id= client_id,
                                                               client_secret= client_secret_id)) 
# -------------------------------

    def new_call(self):
        self.call_counter = self.call_counter+1
        
        if ((self.call_counter%1000) == 0):
            print("Number of calls: ", self.call_counter)

# -------------------------------

    def unknown_artist(self):
        self.unknown_artists = self.unknown_artists+1
            
# -------------------------------

    def single_song_features(self,song):
        '''
        This function gets the audio features from a song
        '''   
        self.new_call()
        
        my_dict = self.sp.audio_features(song['uri'].values[0])[0] # you can provide a list of uri's

        return pd.DataFrame([my_dict])
    
    
# -------------------------------

    def get_songs(self, songs_list):
        '''
        This function retrieves from Spotify the songs specified 

        Input:

        it has to be a dataframe with columns:
            - name
            - artists

        Output:

        A dataframe with the songs and spoty song-codes
        '''
        song_list = pd.DataFrame()

        for idx in range(songs_list.shape[0]):
            song = songs_list.loc[[idx]]

            try:
                song_aux = self.search_song(song_name_fun = song.name[idx], 
                                               artist_name_fun = song.artists[idx][0], 
                                               results_lim = 10,
                                               drop_song = True)   
                if (type(song_aux) != int):
                    song_list = pd.concat([song_list,song_aux])

            except:
                print("Error in song: ",song.name[idx])

        song_list.reset_index(inplace = True, drop = True)

        return song_list
        
    
# -------------------------------

    def get_audio_features(self,song_list):
        '''
        This function returns the audio features of a list of songs
        inputs:
        - songs_list => list of songs df with a collumn called uri

        output:
        - returns a df with the features of each song
        '''     
        song_list_features = pd.DataFrame()
        
        song_list.reset_index(inplace=True,drop=True)

        for i in range(song_list.shape[0]):
            try:
                song_features = self.single_song_features(song_list.loc[[i]])
                song_list_features = pd.concat([song_list_features, song_features])

            except:
                print('Song name "',song_list.loc[[i]]['song_name'].values[0], '" not able to retrieve features' )

        song_list_features.reset_index(inplace = True, drop = True)
        song_total = pd.concat([song_list, song_list_features], axis = 1)

        return song_total
    
# -------------------------------

    def search_song(self, song_name_fun = None, artist_name_fun = None, results_lim = 1, drop_song = True):
        '''
        This function searchs for a song in the Spotify database using th spotify API

        Inputs:
        - song_name_fun => name of the song we want to search, None by deffault (it will ask for the input)
        - artist_name_fun => name of the artist of the song,  None by default (it will ask you to input the name)
        - results_lim => if 1 it will get the first song, if higher than 1 it will ask the user to select the song 
        - drop_song => if False it asks the user to select the song from a list


        Output:
        - the dataframe of the song selected    
        '''

        if (song_name_fun == None):
            print()
            print('Enter the name of the song:')
            print()
            song_name_fun = input()
            print()

        results = self.sp.search(q = "track:"+song_name_fun, limit=results_lim)
        
        self.new_call()

        if (results != None): 
            def get_song_name(i):
                return results['tracks']['items'][i]['name']

            def get_album_name(i):
                return results['tracks']['items'][i]['album']['name']

            def get_artists_name(i):
                return results['tracks']['items'][i]['artists'][0]['name']

            def get_duration_ms(i):
                return results['tracks']['items'][i]['duration_ms']

            def get_song_uri(i):
                return results['tracks']['items'][i]['uri']

            def get_song_href(i):
                return results['tracks']['items'][i]['href']

            song_list = []
            album_list = []
            artist_list = []
            duration_list = []
            href_list = []
            uri_list = []

            for i in range(len(results['tracks']['items'])):
                song_name = get_song_name(i)
                album_name = get_album_name(i)
                artist_name = get_artists_name(i)
                duration_ms = get_duration_ms(i)
                song_href = get_song_href(i)
                uri = get_song_uri(i)

                song_list.append(song_name)
                album_list.append(album_name)
                artist_list.append(artist_name)
                duration_list.append(duration_ms)
                href_list.append(song_href)
                uri_list.append(uri)

            requested_songs = pd.DataFrame({'song_name':song_list,
                                            'album_name':album_list,
                                            'artist_name':artist_list,
                                            'duration_ms':duration_list, 
                                            'uri':uri_list,
                                            'href':href_list})


            def choose_song(requested_songs):
                '''
                This functions displays the options for the user to choose the correct song       
                '''       
                display(requested_songs.iloc[:,0:3])

                end_while = False
                while (end_while == False):
                    print()
                    num = input("Can you choose the song you are searching using the index num?")
                    if num.isdigit() and int(num) < results_lim and int(num) > -1:
                        print()
                        print("You choose number ", int(num))
                        song_selected = requested_songs.loc[[int(num)]]
                        end_while = True
                    else:
                        print()
                        print("Please introdice a correct value")

                display(song_selected)
                return song_selected



            selected = False
            if (results_lim > 1):
                if (artist_name_fun != None):
                    for idx in range(requested_songs.shape[0]):
                        song = requested_songs.loc[[idx]]          
                        if ((song.artist_name[idx].lower() in artist_name_fun.lower()) or (artist_name_fun.lower() in song.artist_name[idx].lower())):
                            song_selected = song
                            selected = True

                if (selected == False):
                    self.unknown_artist()
                    if (artist_name_fun != None):
                        pass
#                       print("Could not find the artist: ", artist_name_fun, "for the song ", song_name_fun)
                    
                    if (drop_song == True):
                        song_selected = 0 
                    else:
                        song_selected = choose_song(requested_songs)

            else:
                song_selected = requested_songs

            return song_selected
        
        print("Song",song_name_fun ,"not found")
        return 0
    
# -------------------------------

    def song_recommender(self, hot100, nothot, scaler, kmeans):

        '''
        This function is used to perform a song recommendation from a song proposed by the user
        
        inputs:
        
        hot100 -> df with the hot 100 songs
        nothot -> df with more songs
        scaler -> scaler used for the model
        kmeans -> model used for clustering
        '''
        song_selected = self.search_song(song_name_fun = None, # asks you to input
                                            artist_name_fun = None, # asks you to select
                                            results_lim = 5, # number of choices
                                            drop_song = False) # it lets you choose if it cannot find it

        song_features = self.get_audio_features(song_selected)

        X = song_features[['duration_ms','danceability', 'energy',
                   'loudness', 'mode', 'speechiness',
                   'acousticness', 'instrumentalness', 'liveness',
                   'valence', 'tempo', 'time_signature']]

        X = X.iloc[:,1:]


        # Transform
        X_scaled = scaler.transform(X)
        X_scaled_df = pd.DataFrame(X_scaled, columns = X.columns)


        # Get the cluster
        if ('DBSCAN' in str(type(kmeans))):
            song_cluster = kmeans.fit_predict(X_scaled_df)[0]
        else:
            song_cluster = kmeans.predict(X_scaled_df)[0]


        song_name = song_selected.song_name[0]
        artist_name = song_selected.artist_name[0]


        finish = 'n'


        while (finish != 'y'):
            print()
            print()
            print("--------------------------------------------------------------------------------------------------")  
            print("------------------------------------ YOUR RECOMMENDATION -----------------------------------------")  
            print("--------------------------------------------------------------------------------------------------")  
            print()
            print()
            
            if any(hot100.song_name == song_name):
                print()
                print("#### Its hot!              ")

                hot100_cluster = hot100[hot100.cluster == song_cluster]

                if (hot100_cluster.shape[0] > 1):  
                    display(hot100_cluster.sample())   

                else:
                    print("       But no more similar hot songs            ")
                    nothot_cluster = nothot[nothot.cluster == song_cluster]
                    display(nothot_cluster.sample())   


            else:
                nothot_cluster = nothot[nothot.cluster == song_cluster]
                display(nothot_cluster.sample())

            print()
            print()
            print("Are you ok with this option? (y) to confirm ")
            print()    

            finish = input()