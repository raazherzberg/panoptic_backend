import nltk, string
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.cluster import AffinityPropagation

punctuation_map = dict((ord(char), None) for char in string.punctuation)
stemmer = nltk.stem.PorterStemmer()

def stem_tokens(tokens):
    return [stemmer.stem(item) for item in tokens] #gave up on steming for now
    #return [item for item in tokens]

def normalize(text):
    return stem_tokens(nltk.word_tokenize(text.lower().translate(punctuation_map)))

vectorizer = TfidfVectorizer(tokenizer=normalize)

def get_clusters(sentences):
    tf_idf_matrix = vectorizer.fit_transform(sentences)
    similarity_matrix = (tf_idf_matrix * tf_idf_matrix.T).A
    affinity_propagation = AffinityPropagation(affinity="euclidean", damping=0.5)
    affinity_propagation.fit(similarity_matrix)

    labels = affinity_propagation.labels_
    cluster_centers = affinity_propagation.cluster_centers_indices_

    tagged_sentences = zip(sentences, labels)
    clusters = {}

    for sentence, cluster_id in tagged_sentences:
        clusters.setdefault(sentences[cluster_centers[cluster_id]], []).append(sentence)

    return clusters


sentences = [
    'What Trump has said about North Korea',
    'Before a North Korea war, wed see this',
    'Can US shoot down North Korean missiles?',
    'Wat? Susan Rice Urges Trump to Tolerate Nuclear Weapons in North Korea',
    'North Korean Standoff Has Tough Path to Resolution',
    'Italy Sees Signs of Migrant Tide Turning',
    'Italy Releases evidance of open boarders ngo taking migrants from human trafficares',
    'U.S. on North Korea: Were Speaking With One Voice',
    'John Kerry reassures Kenyans vote was not rigged',
    'Opposition Leader Claims Fraud in Kenya Election'
]

clusters = get_clusters(sentences)
for cluster in clusters:
    print cluster + ":"
    for element in clusters[cluster]:
        print(element)
    print "       "
    #print(cluster, ':')
    #for element in clusters[cluster]:
    #    print('  - ', element)