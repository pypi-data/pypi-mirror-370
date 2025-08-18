from golpo import Golpo
import time 

golpo_client = Golpo(api_key='96gkPmRejr1nLClgLpxHc3YlfpBP8IsW6Ptom6mT')

start_time = time.time()
new_script = "Hello my name is Shreyas"
podcast_url, podcast_script = golpo_client.create_video(
    prompt='summarize',
    uploads=['/Users/shreyas/Downloads/MSCS-2223-AI.pdf'], 
    timing='0.25',
    include_watermark=False,
    output_volume=2.0,
)
end_time = time.time()
print(f'time elapsed {end_time - start_time}')
print("******")
print(podcast_url)
print("********")
print(podcast_script)
print("**********")
