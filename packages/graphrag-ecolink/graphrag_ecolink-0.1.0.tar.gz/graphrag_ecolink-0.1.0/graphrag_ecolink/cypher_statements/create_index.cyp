
CREATE VECTOR INDEX FOR (c:__Chunk__) ON (c.text_embedding)
OPTIONS {
  indexConfig: {
    `vector.dimensions`: 384,
    `vector.similarity_function`: "cosine"
  }
};

CREATE VECTOR INDEX entity_title_desc_index FOR (e:__Entity__) ON (e.title_description_embedding)
OPTIONS {
  indexConfig: {
    `vector.dimensions`: 1536,
    `vector.similarity_function`: "cosine"
  }
};


CREATE VECTOR INDEX FOR ()- [r:RELATED] -() ON (r.description_embedding)
OPTIONS {
  indexConfig: {
    `vector.dimensions`: 384,
    `vector.similarity_function`: "cosine"
  }
};


CREATE VECTOR INDEX FOR (c:__Community__)  ON (c.title_embedding)
OPTIONS {
  indexConfig: {
    `vector.dimensions`: 384,
    `vector.similarity_function`: "cosine"
  }
};

CREATE VECTOR INDEX FOR (c:__Community__)  ON (c.summary_embedding)
OPTIONS {
  indexConfig: {
    `vector.dimensions`: 384,
    `vector.similarity_function`: "cosine"
  }
};

CREATE VECTOR INDEX FOR (c:__Community__)  ON (c.full_content_embedding)
OPTIONS {
  indexConfig: {
    `vector.dimensions`: 384,
    `vector.similarity_function`: "cosine"
  }
};

