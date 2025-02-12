import csv
import itertools
import sys

PROBS = {

    # Unconditional probabilities for having gene
    "gene": {
        2: 0.01,
        1: 0.03,
        0: 0.96
    },

    "trait": {

        # Probability of trait given two copies of gene
        2: {
            True: 0.65,
            False: 0.35
        },

        # Probability of trait given one copy of gene
        1: {
            True: 0.56,
            False: 0.44
        },

        # Probability of trait given no gene
        0: {
            True: 0.01,
            False: 0.99
        }
    },

    # Mutation probability
    "mutation": 0.01
}


def main():

    # Check for proper usage
    if len(sys.argv) != 2:
        sys.exit("Usage: python heredity.py data.csv")
    people = load_data(sys.argv[1])

    # Keep track of gene and trait probabilities for each person
    probabilities = {
        person: {
            "gene": {
                2: 0,
                1: 0,
                0: 0
            },
            "trait": {
                True: 0,
                False: 0
            }
        }
        for person in people
    }

    # Loop over all sets of people who might have the trait
    names = set(people)
    for have_trait in powerset(names):

        # Check if current set of people violates known information
        fails_evidence = any(
            (people[person]["trait"] is not None and
             people[person]["trait"] != (person in have_trait))
            for person in names
        )
        if fails_evidence:
            continue

        # Loop over all sets of people who might have the gene
        for one_gene in powerset(names):
            for two_genes in powerset(names - one_gene):

                # Update probabilities with new joint probability
                p = joint_probability(people, one_gene, two_genes, have_trait)
                update(probabilities, one_gene, two_genes, have_trait, p)

    # Ensure probabilities sum to 1
    normalize(probabilities)

    # Print results
    for person in people:
        print(f"{person}:")
        for field in probabilities[person]:
            print(f"  {field.capitalize()}:")
            for value in probabilities[person][field]:
                p = probabilities[person][field][value]
                print(f"    {value}: {p:.4f}")


def load_data(filename):
    """
    Load gene and trait data from a file into a dictionary.
    File assumed to be a CSV containing fields name, mother, father, trait.
    mother, father must both be blank, or both be valid names in the CSV.
    trait should be 0 or 1 if trait is known, blank otherwise.
    """
    data = dict()
    with open(filename) as f:
        reader = csv.DictReader(f)
        for row in reader:
            name = row["name"]
            data[name] = {
                "name": name,
                "mother": row["mother"] or None,
                "father": row["father"] or None,
                "trait": (True if row["trait"] == "1" else
                          False if row["trait"] == "0" else None)
            }
    return data


def powerset(s):
    """
    Return a list of all possible subsets of set s.
    """
    s = list(s)
    return [
        set(s) for s in itertools.chain.from_iterable(
            itertools.combinations(s, r) for r in range(len(s) + 1)
        )
    ]


def joint_probability(people, one_gene, two_genes, have_trait):
    """
    Compute and return a joint probability.

    The probability returned should be the probability that
        * everyone in set `one_gene` has one copy of the gene, and
        * everyone in set `two_genes` has two copies of the gene, and
        * everyone not in `one_gene` or `two_gene` does not have the gene, and
        * everyone in set `have_trait` has the trait, and
        * everyone not in set` have_trait` does not have the trait.
    """
    probability = 1

    # Calculate probability for each person
    for person in people:
        # Get number of genes for this person in this scenario
        num_genes = 2 if person in two_genes else 1 if person in one_gene else 0
        
        # Check if person has trait in this scenario
        has_trait = person in have_trait
        
        # Get person's parents
        mother = people[person]["mother"]
        father = people[person]["father"]
        
        # Calculate gene probability
        if mother is None and father is None:
            # No parents - use unconditional probability
            gene_prob = PROBS["gene"][num_genes]
        else:
            # Has parents - calculate inheritance probability
            # First determine parents' number of genes
            mother_genes = 2 if mother in two_genes else 1 if mother in one_gene else 0
            father_genes = 2 if father in two_genes else 1 if father in one_gene else 0
            
            # Probability of getting gene from each parent
            # For each parent: probability they pass the gene depends on how many copies they have
            mother_pass = (
                1.0 if mother_genes == 2 else  # Always passes if 2 copies
                0.5 if mother_genes == 1 else  # 50% chance if 1 copy
                0.0                           # Never passes if 0 copies
            )
            father_pass = (
                1.0 if father_genes == 2 else  # Always passes if 2 copies
                0.5 if father_genes == 1 else  # 50% chance if 1 copy
                0.0                           # Never passes if 0 copies
            )
            
            # Account for mutation
            mother_pass = (1 - PROBS["mutation"]) * mother_pass + PROBS["mutation"] * (1 - mother_pass)
            father_pass = (1 - PROBS["mutation"]) * father_pass + PROBS["mutation"] * (1 - father_pass)
            
            if num_genes == 2:
                # Need gene from both parents
                gene_prob = mother_pass * father_pass
            elif num_genes == 1:
                # Need gene from exactly one parent
                gene_prob = (mother_pass * (1-father_pass) + 
                           (1-mother_pass) * father_pass)
            else:
                # Need no gene from either parent
                gene_prob = (1-mother_pass) * (1-father_pass)
        
        # Get trait probability based on number of genes
        trait_prob = PROBS["trait"][num_genes][has_trait]
        
        # Multiply probabilities
        probability *= gene_prob * trait_prob
    
    return probability


def update(probabilities, one_gene, two_genes, have_trait, p):
    """
    Add to `probabilities` a new joint probability `p`.
    Each person should have their "gene" and "trait" distributions updated.
    Which value for each distribution is updated depends on whether
    the person is in `have_gene` and `have_trait`, respectively.
    """
    for person in probabilities:
        # Update gene probability
        if person in two_genes:
            probabilities[person]["gene"][2] += p
        elif person in one_gene:
            probabilities[person]["gene"][1] += p
        else:
            probabilities[person]["gene"][0] += p
            
        # Update trait probability
        probabilities[person]["trait"][person in have_trait] += p


def normalize(probabilities):
    """
    Update `probabilities` such that each probability distribution
    is normalized (i.e., sums to 1, with relative proportions the same).
    """
    for person in probabilities:
        # Normalize gene distribution
        gene_total = sum(probabilities[person]["gene"].values())
        for gene in probabilities[person]["gene"]:
            probabilities[person]["gene"][gene] /= gene_total
            
        # Normalize trait distribution
        trait_total = sum(probabilities[person]["trait"].values())
        for trait in probabilities[person]["trait"]:
            probabilities[person]["trait"][trait] /= trait_total


if __name__ == "__main__":
    main()
