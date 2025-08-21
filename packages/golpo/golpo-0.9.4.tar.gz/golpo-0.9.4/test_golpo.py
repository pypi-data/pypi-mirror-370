from golpo import Golpo
import time 

golpo_client = Golpo(api_key='fK8TYM222411BH4Bd9oUf6s99Op58Gvq1LIbJJKe')

start_time = time.time()
new_script = "Hello my name is Shreyas"
podcast_url, podcast_script = golpo_client.create_podcast(
    prompt='what is the point of education',
    style='solo-male'
)
end_time = time.time()
print(f'time elapsed {end_time - start_time}')
print("******")
print(podcast_url)
print("********")
print(podcast_script)
print("**********")
