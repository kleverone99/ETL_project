-- DROP TABLE author;
CREATE TABLE author
(
    author_id integer NOT NULL,
    name character varying COLLATE pg_catalog."default" NOT NULL,
    born date,
    description character varying COLLATE pg_catalog."default",
    CONSTRAINT author_pkey PRIMARY KEY (author_id)
);
-- DROP TABLE quote
CREATE TABLE quote
(
    quote_id integer NOT NULL,
    quote_text character varying COLLATE pg_catalog."default",
    author_name character varying COLLATE pg_catalog."default",
    CONSTRAINT quote_pkey PRIMARY KEY (quote_id)
);

-- DROP TABLE tag;
CREATE TABLE tag
(
    quote_id integer NOT NULL,
    tag character varying COLLATE pg_catalog."default",
    CONSTRAINT tag_quote_id_fkey FOREIGN KEY (quote_id)
        REFERENCES public.quote (quote_id) MATCH SIMPLE
        ON UPDATE NO ACTION
        ON DELETE NO ACTION
)

