# This file contains the options that you should modify to solve Question 2

# IMPORTANT NOTE:
# Comment your code explaining why you chose the values you chose.
# Uncommented code will be penalized.


def question2_1():
    # noise=0: Agent moves deterministically
    # discount_factor=0.3: Heavily discount future rewards to prefer closer +1
    # living_reward=-1: Small penalty for living to encourage quick path
    return {
        "noise": 0,
        "discount_factor": 0.3,
        "living_reward": -1
    }

def question2_2():
    # noise=0.2: Agent moves slightly deterministically it didnt work if the noise was 0
    # discount_factor=0.3: Heavily discount future rewards to prefer closer +1
    # living_reward=-0.1: Tiny penalty makes longer path acceptable
    return {
        "noise": 0.2,
        "discount_factor": 0.3,
        "living_reward": -0.1
    }

def question2_3():
    # noise=0: Agent moves deterministically
    # discount_factor=0.9: Value future rewards to seek +10
    # living_reward=-1: Penalty encourages quick dangerous path
    return {
        "noise": 0,
        "discount_factor": 0.9,
        "living_reward": -1
    }

def question2_4():
    # noise=0.2: Added some noise so that the agent can explore more
    # discount_factor=1: Value future rewards to seek +10
    # living_reward=-0.01: Small penalty makes safe path viable
    return {
        "noise": 0.2,
        "discount_factor": 1,
        "living_reward": -0.01
    }

def question2_5():
    # noise=0: Agent moves deterministically
    # discount_factor=0.9: Consider future rewards
    # living_reward=50: Positive reward makes living valuable
    return {
        "noise": 0,
        "discount_factor": 0.9,
        "living_reward": 50
    }

def question2_6():
    # noise=0: Agent moves deterministically
    # discount_factor=0.9: Consider future rewards
    # living_reward=-50: Heavy penalty forces quick termination
    return {
        "noise": 0,
        "discount_factor": 0.9,
        "living_reward": -50
    }