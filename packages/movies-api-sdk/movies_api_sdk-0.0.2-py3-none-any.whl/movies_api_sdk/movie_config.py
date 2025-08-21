import os
from dotenv import load_dotenv

load_dotenv()


class MovieConfig:
    """
    Classe de configuration contenant les paramètres pour le client SDK.
    Inclut l'URL de base et les options de backoff progressif.
    """

    movie_base_url: str
    movie_backoff: bool
    movie_backoff_max_time: int

    def __init__(
        self,
        movie_base_url: str = None,
        backoff: bool = True,
        backoff_max_time: int = 30,
    ):
        """
        Constructeur pour la classe de configuration.

        Args:
            movie_base_url (str, optional):
                L'URL de base à utiliser pour tous les appels d'API.
                Peut être transmise directement ou définie via la variable
                d'environnement `MOVIE_API_BASE_URL`.
            backoff (bool):
                Indique si le SDK doit réessayer un appel en utilisant
                un backoff progressif en cas d'erreurs.
            backoff_max_time (int):
                Temps maximal (en secondes) pendant lequel le SDK doit
                continuer à réessayer avant d'abandonner.
        """
        self.movie_base_url = movie_base_url or os.getenv("MOVIE_API_BASE_URL")
        print(f"MOVIE_API_BASE_URL in MovieConfig init: {self.movie_base_url}")

        if not self.movie_base_url:
            raise ValueError(
                "L'URL de base est requise. "
                "Définissez la variable d'environnement MOVIE_API_BASE_URL."
            )

        self.movie_backoff = backoff
        self.movie_backoff_max_time = backoff_max_time

    def __str__(self):
        """
        Représentation lisible de la configuration (pour la journalisation).
        """
        return f"{self.movie_base_url} {self.movie_backoff} {self.movie_backoff_max_time}"
