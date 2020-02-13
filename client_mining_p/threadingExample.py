import hashlib
import requests
import multiprocessing
import random
import sys
import json
import time
import psutil


def proof_of_work(block, thread_number, valid_guesses):
    """
    Simple Proof of Work Algorithm
    Stringify the block and look for a proof.
    Loop through possibilities, checking each one against `valid_proof`
    in an effort to find a number that is a valid proof
    :return: A valid proof for the provided block
    """
    #     Simple Proof of Work Algorithm
    #     Stringify the block and look for a proof.
    #     Loop through possibilities, checking each one against `valid_proof`
    #     in an effort to find a number that is a valid proof
    #     :return: A valid proof for the provided block
    #     """
    #     # TODO

    block_string = json.dumps(block, sort_keys = True)
    guess = thread_number * 1000000000
    not_valid = True
    while not_valid:
        if valid_proof(block_string, guess):
            not_valid = False
        else:
            guess += 1
    valid_guesses[thread_number] = guess


def valid_proof(block_string, proof):
    """
    Validates the Proof:  Does hash(block_string, proof) contain 6
    leading zeroes?  Return true if the proof is valid
    :param block_string: <string> The stringified block to use to
    check in combination with `proof`
    :param proof: <int?> The value that when combined with the
    stringified previous block results in a hash that has the
    correct number of leading zeroes.
    :return: True if the resulting hash is a valid proof, False otherwise
    """
    guess = f'{block_string}{proof}'.encode()
    guess_hash = hashlib.sha256(guess).hexdigest()
    # return True or False
    return guess_hash[:6] == "000000"


if __name__ == '__main__':
    # What is the server address? IE `python3 miner.py https://server.com/api/`

    if len(sys.argv) > 1:
        node = sys.argv[1]
    else:
        node = "http://localhost:5000"

    # Load ID
    f = open("my_id.txt", "r")
    id = f.read()
    print("ID is", id)
    f.close()
    random.seed(time.gmtime())
    count = 0
    proofs = []
    # Run forever until interrupted
    while True:
        r = requests.get(url = node + "/last_block")
        # Handle non-json response
        try:
            data = r.json()
        except ValueError:
            print("Error:  Non-json response")
            print("Response returned:")
            print(r)
            break

        # TODO: Get the block from `data` and use it to look for a new proof

        threads = []
        print(f'CPU percent {psutil.cpu_percent()}')
        manager = multiprocessing.Manager()
        valid_guesses = manager.dict()
        for i in range(6):
            thread = multiprocessing.Process(target = proof_of_work,
                                             args = (data['last_block'], i,
                                                     valid_guesses))
            threads.append(thread)
            thread.start()
        valid_guess = False
        while not valid_guess:
            for proc in threads:
                if not proc.is_alive():
                    valid_guess = True

        for proc in threads:
            if proc.is_alive():
                proc.terminate()
                proc.join()

        valid_guess = valid_guesses.values()
        proof = valid_guess[0]
        post_data = {"proof": valid_guess[0], "id": id}

        r = requests.post(url = node + "/mine", json = post_data)
        data = r.json()

        # TODO: If the server responds with a 'message' 'New Block Forged'
        # add 1 to the number of coins mined and print it.  Otherwise,
        # print the message from the server.
        if data["message"] == "New Block Forged":
            count += 1
            print(
                "You mined a block: Total number of blocks mined: " + f'{count}')
        else:
            print(data["message"])
