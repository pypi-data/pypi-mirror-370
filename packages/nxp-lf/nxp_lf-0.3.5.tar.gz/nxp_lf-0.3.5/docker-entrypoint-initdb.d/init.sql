--
-- PostgreSQL database dump
--

-- Dumped from database version 12.6 (Debian 12.6-1.pgdg100+1)
-- Dumped by pg_dump version 12.6 (Debian 12.6-1.pgdg100+1)

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
-- Name: lf_history; Type: TABLE; Schema: public; Owner: fadmin
--

CREATE TABLE public.lf_history (
    id integer NOT NULL,
    build_plan character varying,
    build_number integer,
    platform character varying,
    scope character varying,
    testcase character varying,
    result integer,
    testcase_log text NULL
);


ALTER TABLE public.lf_history OWNER TO fadmin;

--
-- Name: lf_history_id_seq; Type: SEQUENCE; Schema: public; Owner: fadmin
--

CREATE SEQUENCE public.lf_history_id_seq
    AS integer
    START WITH 1
    INCREMENT BY 1
    NO MINVALUE
    NO MAXVALUE
    CACHE 1;


ALTER TABLE public.lf_history_id_seq OWNER TO fadmin;

--
-- Name: lf_history_id_seq; Type: SEQUENCE OWNED BY; Schema: public; Owner: fadmin
--

ALTER SEQUENCE public.lf_history_id_seq OWNED BY public.lf_history.id;


--
-- Name: lf_history_meta; Type: TABLE; Schema: public; Owner: fadmin
--

CREATE TABLE public.lf_history_meta (
    id integer NOT NULL,
    scope character varying,
    head integer,
    head_1 integer
);


ALTER TABLE public.lf_history_meta OWNER TO fadmin;

--
-- Name: lf_history_meta_id_seq; Type: SEQUENCE; Schema: public; Owner: fadmin
--

CREATE SEQUENCE public.lf_history_meta_id_seq
    AS integer
    START WITH 1
    INCREMENT BY 1
    NO MINVALUE
    NO MAXVALUE
    CACHE 1;


ALTER TABLE public.lf_history_meta_id_seq OWNER TO fadmin;

--
-- Name: lf_history_meta_id_seq; Type: SEQUENCE OWNED BY; Schema: public; Owner: fadmin
--

ALTER SEQUENCE public.lf_history_meta_id_seq OWNED BY public.lf_history_meta.id;


--
-- Name: lf_history_ss; Type: TABLE; Schema: public; Owner: fadmin
--

CREATE TABLE public.lf_history_ss (
    id integer NOT NULL,
    scope character varying,
    platform character varying,
    testcase character varying,
    lastpass integer,
    lastpass_1 integer
);


ALTER TABLE public.lf_history_ss OWNER TO fadmin;

--
-- Name: lf_history_ss_id_seq; Type: SEQUENCE; Schema: public; Owner: fadmin
--

CREATE SEQUENCE public.lf_history_ss_id_seq
    AS integer
    START WITH 1
    INCREMENT BY 1
    NO MINVALUE
    NO MAXVALUE
    CACHE 1;


ALTER TABLE public.lf_history_ss_id_seq OWNER TO fadmin;

--
-- Name: lf_history_ss_id_seq; Type: SEQUENCE OWNED BY; Schema: public; Owner: fadmin
--

ALTER SEQUENCE public.lf_history_ss_id_seq OWNED BY public.lf_history_ss.id;


--
-- Name: lf_history id; Type: DEFAULT; Schema: public; Owner: fadmin
--

ALTER TABLE ONLY public.lf_history ALTER COLUMN id SET DEFAULT nextval('public.lf_history_id_seq'::regclass);


--
-- Name: lf_history_meta id; Type: DEFAULT; Schema: public; Owner: fadmin
--

ALTER TABLE ONLY public.lf_history_meta ALTER COLUMN id SET DEFAULT nextval('public.lf_history_meta_id_seq'::regclass);


--
-- Name: lf_history_ss id; Type: DEFAULT; Schema: public; Owner: fadmin
--

ALTER TABLE ONLY public.lf_history_ss ALTER COLUMN id SET DEFAULT nextval('public.lf_history_ss_id_seq'::regclass);


--
-- Name: lf_history lf_history_build_number_platform_scope_testcase_key; Type: CONSTRAINT; Schema: public; Owner: fadmin
--

ALTER TABLE ONLY public.lf_history
    ADD CONSTRAINT lf_history_build_number_platform_scope_testcase_key UNIQUE (build_number, platform, scope, testcase);


--
-- Name: lf_history_meta lf_history_meta_pkey; Type: CONSTRAINT; Schema: public; Owner: fadmin
--

ALTER TABLE ONLY public.lf_history_meta
    ADD CONSTRAINT lf_history_meta_pkey PRIMARY KEY (id);


--
-- Name: lf_history_meta lf_history_meta_scope_key; Type: CONSTRAINT; Schema: public; Owner: fadmin
--

ALTER TABLE ONLY public.lf_history_meta
    ADD CONSTRAINT lf_history_meta_scope_key UNIQUE (scope);


--
-- Name: lf_history lf_history_pkey; Type: CONSTRAINT; Schema: public; Owner: fadmin
--

ALTER TABLE ONLY public.lf_history
    ADD CONSTRAINT lf_history_pkey PRIMARY KEY (id);


--
-- Name: lf_history_ss lf_history_ss_pkey; Type: CONSTRAINT; Schema: public; Owner: fadmin
--

ALTER TABLE ONLY public.lf_history_ss
    ADD CONSTRAINT lf_history_ss_pkey PRIMARY KEY (id);


--
-- Name: lf_history_ss lf_history_ss_scope_platform_testcase_key; Type: CONSTRAINT; Schema: public; Owner: fadmin
--

ALTER TABLE ONLY public.lf_history_ss
    ADD CONSTRAINT lf_history_ss_scope_platform_testcase_key UNIQUE (scope, platform, testcase);


--
-- PostgreSQL database dump complete
--

