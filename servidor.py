from fastapi import FastAPI, HTTPException
from pydantic import BaseModel
import aiohttp
import asyncio
import uvicorn

app = FastAPI()

OMDB_API_KEY = "9cbc0438"
TMDB_TOKEN = "eyJhbGciOiJIUzI1NiJ9.eyJhdWQiOiI2Zjc1ZGU0MWE1ZjQ0NWYxY2Q3YTc3YjVmNmUyYjJjOCIsIm5iZiI6MTc0MzQ1MzY0Mi40MzkwMDAxLCJzdWIiOiI2N2VhZmRjYWI4MmY3ZjdkZDMyNDUzYzkiLCJzY29wZXMiOlsiYXBpX3JlYWQiXSwidmVyc2lvbiI6MX0.YYwUNcaRk_z8G1m764j5STvpnbInEZfqE1mVS01ESN0"

class MovieRequest(BaseModel):
    titulo: str
    ano: int

@app.post("/movie")
async def get_movie(movie_req: MovieRequest):
    titulo = movie_req.titulo
    ano = movie_req.ano

    async with aiohttp.ClientSession() as session:
        omdb_url = f"http://www.omdbapi.com/?t={titulo}&y={ano}&apikey={OMDB_API_KEY}"
        tmdb_url = f"https://api.themoviedb.org/3/search/movie?query={titulo}&year={ano}"
        headers_tmdb = {
            "accept": "application/json",
            "Authorization": f"Bearer {TMDB_TOKEN}"
        }

        async def fetch_omdb():
            async with session.get(omdb_url) as resp:
                return await resp.json()

        async def fetch_tmdb_search():
            async with session.get(tmdb_url, headers=headers_tmdb) as resp:
                return await resp.json()

        omdb_data, tmdb_search_data = await asyncio.gather(fetch_omdb(), fetch_tmdb_search())

        if omdb_data.get("Response") == "False":
            raise HTTPException(status_code=404, detail="Filme não encontrado na OMDB")
        sinopse = omdb_data.get("Plot", "Sinopse não disponível")

        results = tmdb_search_data.get("results")
        if not results:
            reviews = []
        else:
            movie_id = results[0]["id"]
            tmdb_reviews_url = f"https://api.themoviedb.org/3/movie/{movie_id}/reviews?language=en-US&page=1"
            async with session.get(tmdb_reviews_url, headers=headers_tmdb) as resp:
                tmdb_reviews_data = await resp.json()

            reviews_results = tmdb_reviews_data.get("results", [])
            reviews = [review.get("content", "") for review in reviews_results][:3]

    return {
        "titulo": titulo,
        "ano": ano,
        "sinopse": sinopse,
        "reviews": reviews
    }

if __name__ == "__main__":
    uvicorn.run(app, host="0.0.0.0", port=8000)
