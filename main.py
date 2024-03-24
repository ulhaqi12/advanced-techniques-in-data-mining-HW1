import getopt
import sys
import itertools
from tqdm import tqdm


def split_line_into_items(line):
    return set([] if line == '' else line.split(' '))


def filter_frequent_items(item_frequencies, min_support):
    return {item: count for item, count in item_frequencies.items() if count >= min_support}


def generate_candidate_combinations(qualified_items, combination_length):
    potential_combinations = {}
    for combination in tqdm(itertools.combinations(sorted(qualified_items), combination_length)):
        potential_combinations[combination] = 0
    return potential_combinations


def tally_combinations(sets_of_items, potential_combinations, combination_length, relevant_items):
    for item_set in tqdm(sets_of_items):
        filtered_items = sorted([item for item in item_set if item in relevant_items])
        combinations = itertools.combinations(filtered_items, combination_length)
        for combination in combinations:
            if combination in potential_combinations:
                potential_combinations[combination] += 1


def discover_frequent_pairs(item_sets, frequent_single_items, min_support):

    potential_pairs = generate_candidate_combinations(frequent_single_items, 2)
    tally_combinations(item_sets, potential_pairs, 2, frequent_single_items)
    return filter_frequent_items(potential_pairs, min_support)


def identify_frequent_triples(item_sets, frequent_item_pairs, min_support):
    relevant_items = set([item for pair in frequent_item_pairs for item in pair])
    potential_triples = generate_candidate_combinations(relevant_items, 3)
    tally_combinations(item_sets, potential_triples, 3, relevant_items)
    return filter_frequent_items(potential_triples, min_support)


def calculate_confidence(base, extension):
    return extension / base


def evaluate_pair_confidence(frequent_items, frequent_pairs):
    confidence_scores = []
    for pair, count in frequent_pairs.items():
        confidence_scores.append(((pair[0], pair[1]), calculate_confidence(frequent_items[pair[0]], count)))
        confidence_scores.append(((pair[1], pair[0]), calculate_confidence(frequent_items[pair[1]], count)))
    return confidence_scores


def evaluate_triple_confidence(frequent_pairs, frequent_triples):
    confidence_list = []
    key_length = len(next(iter(frequent_triples.keys())))
    for triple, count in frequent_triples.items():
        pair_combinations = itertools.combinations(triple, key_length - 1)
        for combination in pair_combinations:
            if combination in frequent_pairs:
                confidence_list.append((tuple(list(combination) + list(set(triple) - set(combination))), calculate_confidence(frequent_pairs[combination], count)))
    return confidence_list



if __name__ == '__main__':
    filepath = 'browsing.txt'
    support_threshold = 100

    print("Processing individual items")
    item_counts = {}
    collections_of_items = []
    with open(filepath, 'r') as file:
        for line in file:
            items_in_line = line.strip().split(' ')
            if items_in_line[0] == '':
                continue
            for item in items_in_line:
                item_counts[item] = item_counts.get(item, 0) + 1
            collections_of_items.append(set(items_in_line))

    qualified_single_items = filter_frequent_items(item_counts, support_threshold)

    print("Identifying frequent item pairs")
    frequent_pairs = discover_frequent_pairs(collections_of_items, qualified_single_items, support_threshold)

    print("Identifying frequent item triples")
    frequent_triples = identify_frequent_triples(collections_of_items, frequent_pairs, support_threshold)

    print("Calculating confidence for item pairs")
    pair_confidence_scores = evaluate_pair_confidence(qualified_single_items, frequent_pairs)
    pair_confidence_scores.sort(key=lambda x: (-x[1], x[0]))

    print("Top 5 item pairs by confidence")
    for pair in pair_confidence_scores[:5]:
        print("{} -> {} with confidence {}".format(pair[0][0], pair[0][1], pair[1]))

    print("Calculating confidence for item triples")
    triple_confidence_scores = evaluate_triple_confidence(frequent_pairs, frequent_triples)
    triple_confidence_scores.sort(key=lambda x: (-x[1], x[0]))
    print("Top 5 item triples by confidence")
    for triple in triple_confidence_scores[:5]:
        print("{}, {} -> {} with confidence {}".format(triple[0][0], triple[0][1], triple[0][2], triple[1]))

    print("Processing complete.")
