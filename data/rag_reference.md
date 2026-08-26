# Trusted Reference: Introduction to RAG

## Definition

RAG stands for Retrieval-Augmented Generation.

RAG is a method that combines information retrieval with language generation.

A RAG system first retrieves relevant information from an external knowledge source. It then provides that information to a language model as context. The language model uses that context to generate a response.

## Why RAG is useful

A language model may not have access to a company's private documents, recent information, or a specific collection of knowledge.

RAG allows an application to retrieve relevant information from an external source and provide it to the model when answering a question.

## Basic RAG workflow

A simplified RAG workflow contains these steps:

1. The user asks a question.

2. The system searches a knowledge source for information related to the question.

3. The system retrieves the most relevant pieces of information.

4. The retrieved information is provided to the language model as context.

5. The language model generates an answer using the retrieved context.

## Retrieval

Retrieval means finding information that is relevant to a user's question.

A knowledge source can contain documents, articles, company policies, manuals, or other information.

## Context

Context is the information given to the language model to help it produce a better answer.

In RAG, the retrieved information becomes part of the context used for generation.

## Generation

Generation is the process where the language model produces a response.

In a RAG system, the model can use the retrieved information as part of its input when generating the answer.

## Embeddings

Embeddings are numerical representations of text that capture relationships between pieces of information.

They can be used to help a system find text that is semantically similar to a user's question.

## Vector database

A vector database can store vector representations of information and support similarity-based searches.

RAG systems can use vector databases as one way to retrieve relevant information.

## RAG is not retraining

RAG does not mean that the language model is retrained every time a user asks a question.

Instead, relevant information is retrieved at query time and provided to the model as context.

## Example

Imagine a company has hundreds of internal policy documents.

An employee asks:

"What is our work-from-home policy?"

A RAG system can search the company's policy documents, retrieve the relevant section, provide it to the language model, and generate an answer based on that information.

## Limitations

RAG does not automatically guarantee that every answer will be correct.

Problems can occur if:

- the relevant information cannot be retrieved
- the retrieved information is incomplete
- the source documents contain incorrect information
- too much irrelevant information is retrieved
- the model misunderstands the retrieved context

Good retrieval and good source data are therefore important.

## Important distinction

RAG is different from simply asking a language model a question without providing external retrieved information.

The key idea is:

User question
→ retrieve relevant information
→ provide information as context
→ generate an answer