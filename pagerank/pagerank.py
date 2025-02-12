import os
import random
import re
import sys

DAMPING = 0.85
SAMPLES = 10000


def main():
    if len(sys.argv) != 2:
        sys.exit("Usage: python pagerank.py corpus")
    corpus = crawl(sys.argv[1])
    ranks = sample_pagerank(corpus, DAMPING, SAMPLES)
    print(f"PageRank Results from Sampling (n = {SAMPLES})")
    for page in sorted(ranks):
        print(f"  {page}: {ranks[page]:.4f}")
    ranks = iterate_pagerank(corpus, DAMPING)
    print(f"PageRank Results from Iteration")
    for page in sorted(ranks):
        print(f"  {page}: {ranks[page]:.4f}")


def crawl(directory):
    """
    Parse a directory of HTML pages and check for links to other pages.
    Return a dictionary where each key is a page, and values are
    a list of all other pages in the corpus that are linked to by the page.
    """
    pages = dict()

    # Extract all links from HTML files
    for filename in os.listdir(directory):
        if not filename.endswith(".html"):
            continue
        with open(os.path.join(directory, filename)) as f:
            contents = f.read()
            links = re.findall(r"<a\s+(?:[^>]*?)href=\"([^\"]*)\"", contents)
            pages[filename] = set(links) - {filename}

    # Only include links to other pages in the corpus
    for filename in pages:
        pages[filename] = set(
            link for link in pages[filename]
            if link in pages
        )

    return pages


def transition_model(corpus, page, damping_factor):
    """
    Return a probability distribution over which page to visit next,
    given a current page.

    With probability `damping_factor`, choose a link at random
    linked to by `page`. With probability `1 - damping_factor`, choose
    a link at random chosen from all pages in the corpus.
    """
    # Get the links from the current page via corpus
    links = corpus[page]

    # If links is empty, return a uniform distribution
    if len(links) == 0:
        return {page: 1.0 / len(corpus) for page in corpus}

    # For all pages in the corpus, calculate the probability of choosing a link at random
    # If the page is not in the links, the probability is (1 - damping_factor) / number of links
    # If the page is in the links, the probability is (1 - damping_factor) / number of links + damping_factor / number of links
    # Set all probabilities to (1 - damping_factor) / number of links first, then for each link in links, add damping_factor / number of links to the probability of the link
    probabilities = {}
    for page in corpus:
        probabilities[page] = (1 - damping_factor) / len(corpus)
    for link in links:
        probabilities[link] += damping_factor / len(links)

    return probabilities


def sample_pagerank(corpus, damping_factor, n):
    """
    Return PageRank values for each page by sampling `n` pages
    according to transition model, starting with a page at random.

    Return a dictionary where keys are page names, and values are
    their estimated PageRank value (a value between 0 and 1). All
    PageRank values should sum to 1.
    """
    # Choose the first page at random
    current_page = random.choice(list(corpus.keys()))

    # Initialize the probabilities
    probabilities = transition_model(corpus, current_page, damping_factor)

    # Keep track of the distribution of pages
    distribution = {}
    for page in corpus:
        distribution[page] = 0

    # Update the distribution of pages
    distribution[current_page] += 1

    # For each of the remaining samples, the next sample should be generated from the previous sample based on the previous sample's transition model.
    for _ in range(n - 1):
        probabilities = transition_model(corpus, current_page, damping_factor)
        current_page = random.choices(list(probabilities.keys()), weights=list(probabilities.values()), k=1)[0]
        distribution[current_page] += 1

    # Return the page rank values
    return {page: count / n for page, count in distribution.items()}
    


def iterate_pagerank(corpus, damping_factor):
    """
    Return PageRank values for each page by iteratively updating
    PageRank values until convergence.

    Return a dictionary where keys are page names, and values are
    their estimated PageRank value (a value between 0 and 1). All
    PageRank values should sum to 1.
    """
    N = len(corpus)
    
    # Initialize the page rank values
    page_rank = {}
    for page in corpus:
        page_rank[page] = 1 / N
    
    # For pages with no links, treat them as having links to all pages
    for page in corpus:
        if len(corpus[page]) == 0:
            corpus[page] = set(corpus.keys())

    # Iterate until convergence (values don't change by more than 0.001)
    while True:
        # Keep track of the previous page rank values
        previous_page_rank = page_rank.copy()

        # Update the page rank values for each page
        for page in corpus:
            total = 0
            # Find all pages that link to this page
            for linking_page in corpus:
                if page in corpus[linking_page]:
                    total += previous_page_rank[linking_page] / len(corpus[linking_page])
            
            # Apply PageRank formula
            page_rank[page] = (1 - damping_factor) / N + damping_factor * total

        # Check if the values have converged
        if all(abs(page_rank[page] - previous_page_rank[page]) < 0.001 for page in corpus):
            break

    return page_rank


if __name__ == "__main__":
    main()
