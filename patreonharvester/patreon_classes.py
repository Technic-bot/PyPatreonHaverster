from dataclasses import dataclass, field

@dataclass
class PatreonPost():
    post_id: int
    title: str
    description: str
    post_type: str
    patreon_url: str
    publication_date: str
    filename: str = ''
    download_url: str = ''
    tags: list[str]= field(default_factory=list)

    def __lt__(self, other):
        return self.post_id < other.post_id
