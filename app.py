import pandas as pd
import numpy as np
import spoty_jzar
import cluster_jzar
import pickle
import streamlit as st


# This is the song recommender script.
# I created a song recommender based on the features of the songs. It does the modeling of the data and assigns a cluster number to each song. It is also able to give a new cluster number to each new song. From there it can recommend other songs also depending on the 100-hot-songs list. It follows the schematic that can be found on the end of this document
# by Jordi Zaragoza


# ----------------------------- Grafical Part --------------------------------------------

st.title('🔥The best Song Recommender🔥')

title = st.text_input('Enter your favourite song', 'Billie Jean...')

if st.button('Fire!'):
    repeat = True
else:
    repeat = False

if (title != 'Billie Jean...') and (repeat == True):   
    # ---------------------------- The code --------------------------------------------------


    hot100 = pd.read_csv('data/100hot_clusters_dbscan.csv', index_col=0)
    nothot = pd.read_csv('data/nothot_clusters_dbscan.csv', index_col=0)
    sp_jzar = spoty_jzar.Spoty_jzar()

    #Retrieve the transformer
    filename = "transformer/scaler.pickle" # Path with filename
    scaler = cluster_jzar.load_pickle(filename)

    # Retrieve the model 
    filename = "model/dbscan.pickle" # Path with filename
    dbscan = cluster_jzar.load_pickle(filename)


    # Song recommender 
    song_selected = sp_jzar.search_song(song_name_fun = title, # asks you to input
                                        artist_name_fun = None, # asks you to select
                                        results_lim = 1, # number of choices
                                        drop_song = False) # it lets you choose if it cannot find it
    

    song_features = sp_jzar.get_audio_features(song_selected)

    X = song_features[['duration_ms','danceability', 'energy',
               'loudness', 'mode', 'speechiness',
               'acousticness', 'instrumentalness', 'liveness',
               'valence', 'tempo', 'time_signature']]

    X = X.iloc[:,1:]
 
    
    # Transform
    X_scaled = scaler.transform(X)
    X_scaled_df = pd.DataFrame(X_scaled, columns = X.columns)

    # Get the cluster
    song_cluster = dbscan.fit_predict(X_scaled_df)

    song_name = song_selected.song_name[0]
    artist_name = song_selected.artist_name[0]

    st.write("--------------------------------------------------------------------------------------------------")  
    try:
        if any(hot100.song_name == song_name):
            st.write()
            st.write("           ### Uhhhh, Its hot!              ")

            hot100_cluster = hot100[hot100.cluster == song_cluster]

            if (hot100_cluster.shape[0] > 1):  
                samp = hot100_cluster.sample()  

            else:
                st.write("       But no more similar hot songs            ")
                nothot_cluster = nothot[nothot.cluster == song_cluster]
                samp = nothot_cluster.sample()


        else:
            nothot_cluster = nothot[nothot.cluster == song_cluster]
            samp = nothot_cluster.sample()
    
    except:
        samp = nothot.sample()
        
    st.metric(value=samp.artist_name.values[0], label=samp.song_name.values[0], delta=samp.album_name.values[0])
        
    st.write("--------------------------------------------------------------------------------------------------")
    st.write("#### Are you ok with this option? No? lit the fire again!")
    st.write("--------------------------------------------------------------------------------------------------")  
    

        
        




