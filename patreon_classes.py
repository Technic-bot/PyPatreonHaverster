from dataclasses import dataclass, field, asdict

@dataclass
class PatreonPost():
    post_id: int
    title: str
    description: str
    filename: str
    post_type: str
    download_url: str
    patreon_url: str
    publication_date: str
    tags: list[str]= field(default_factory=list)
