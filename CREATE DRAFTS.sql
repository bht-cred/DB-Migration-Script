--
-- PostgreSQL database dump
--

-- Dumped from database version 12.8
-- Dumped by pg_dump version 14.4

SET statement_timeout = 0;
SET lock_timeout = 0;
SET idle_in_transaction_session_timeout = 0;
SET client_encoding = 'UTF8';
SET standard_conforming_strings = on;
SELECT pg_catalog.set_config('search_path', '', false);
SET check_function_bodies = false;
SET xmloption = content;
SET client_min_messages = warning;
SET row_security = off;

SET default_tablespace = '';

SET default_table_access_method = heap;

--
-- Name: drafts; Type: TABLE; Schema: public; Owner: prod_recovery
--

CREATE TABLE public.drafts (
    id integer NOT NULL,
    draft_id uuid NOT NULL,
    company_id uuid,
    notice_type character varying,
    document_type character varying,
    archive boolean DEFAULT false,
    author character varying,
    role character varying,
    updated timestamp without time zone DEFAULT now(),
    created timestamp without time zone DEFAULT now(),
    draft_name character varying,
    case_type character varying,
    is_vernacular boolean DEFAULT false,
    author_id character varying,
    language character varying,
    s3_path character varying,
    is_deleted boolean DEFAULT false
);


ALTER TABLE public.drafts OWNER TO prod_recovery;

--
-- Name: drafts_id_seq; Type: SEQUENCE; Schema: public; Owner: prod_recovery
--

CREATE SEQUENCE public.drafts_id_seq
    START WITH 1
    INCREMENT BY 1
    NO MINVALUE
    NO MAXVALUE
    CACHE 1;


ALTER TABLE public.drafts_id_seq OWNER TO prod_recovery;

--
-- Name: drafts_id_seq; Type: SEQUENCE OWNED BY; Schema: public; Owner: prod_recovery
--

ALTER SEQUENCE public.drafts_id_seq OWNED BY public.drafts.id;


--
-- Name: drafts id; Type: DEFAULT; Schema: public; Owner: prod_recovery
--

ALTER TABLE ONLY public.drafts ALTER COLUMN id SET DEFAULT nextval('public.drafts_id_seq'::regclass);


--
-- Name: drafts drafts_pkey; Type: CONSTRAINT; Schema: public; Owner: prod_recovery
--

ALTER TABLE ONLY public.drafts
    ADD CONSTRAINT drafts_pkey PRIMARY KEY (draft_id);


--
-- Name: TABLE drafts; Type: ACL; Schema: public; Owner: prod_recovery
--

GRANT SELECT ON TABLE public.drafts TO readaccess;
GRANT ALL ON TABLE public.drafts TO pod_recovery;
GRANT SELECT ON TABLE public.drafts TO dbbackup_user;
GRANT SELECT ON TABLE public.drafts TO prod_read;
GRANT SELECT ON TABLE public.drafts TO gourav_datascience_read;
GRANT SELECT,INSERT,UPDATE ON TABLE public.drafts TO adityagupta;
GRANT SELECT,INSERT,UPDATE ON TABLE public.drafts TO vikramsinha;
GRANT SELECT,INSERT,UPDATE ON TABLE public.drafts TO kartikgautam;
GRANT SELECT,INSERT,UPDATE ON TABLE public.drafts TO gauravagarwal;
GRANT SELECT,INSERT,UPDATE ON TABLE public.drafts TO tarunkumar;
GRANT SELECT,INSERT,UPDATE ON TABLE public.drafts TO nitinupadhyay;
GRANT SELECT,INSERT,UPDATE ON TABLE public.drafts TO mehulmittal;
GRANT SELECT,INSERT,UPDATE ON TABLE public.drafts TO laksh;
GRANT SELECT ON TABLE public.drafts TO sarthakbhutani_read_user;
GRANT SELECT ON TABLE public.drafts TO piyush_read;


--
-- Name: SEQUENCE drafts_id_seq; Type: ACL; Schema: public; Owner: prod_recovery
--

GRANT ALL ON SEQUENCE public.drafts_id_seq TO pod_recovery;
GRANT SELECT,USAGE ON SEQUENCE public.drafts_id_seq TO dbbackup_user;
GRANT SELECT,UPDATE ON SEQUENCE public.drafts_id_seq TO adityagupta;
GRANT SELECT,UPDATE ON SEQUENCE public.drafts_id_seq TO vikramsinha;
GRANT SELECT,UPDATE ON SEQUENCE public.drafts_id_seq TO kartikgautam;
GRANT SELECT,UPDATE ON SEQUENCE public.drafts_id_seq TO gauravagarwal;
GRANT SELECT,UPDATE ON SEQUENCE public.drafts_id_seq TO tarunkumar;
GRANT SELECT,UPDATE ON SEQUENCE public.drafts_id_seq TO nitinupadhyay;
GRANT SELECT,UPDATE ON SEQUENCE public.drafts_id_seq TO mehulmittal;
GRANT ALL ON SEQUENCE public.drafts_id_seq TO sarthakbhutani_read_user;


--
-- PostgreSQL database dump complete
--

➜  ~ 
