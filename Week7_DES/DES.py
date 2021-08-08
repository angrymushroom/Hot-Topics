import random
import simpy


random_seed = 0
new_customers = 10
interval_customers = 10

min_patience = 1
max_patience = 3


def source(env, number, interval, counter):
    """
    Generate customers randomly.

    :param env: environment from simpy.Environment()
    :param number: the number of customers to generate
    :param interval: to generate a timeout
    :param counter: resources of the counters
    """
    for i in range(number):
        c = customer(env, 'Customer%2d' % i, counter, time_in_bank=12.0)
        env.process(c)
        t = random.expovariate(1.0/interval)  # generate the timeout with an exponential distribution
        yield env.timeout(t)  # stop for t seconds


def customer(env, name, counter, time_in_bank):
    """
    Generate the decision of a customer.

    If waiting time is within customer's patience, the customer chooses to wait. Or the customer
    decides to leave.

    :param env: environment
    :param name: the name of a customer e.g. Customer 2
    :param counter: resources of the counters
    :param time_in_bank: to generate the timeout
    """
    arrive = env.now
    print('%3.4f %s here I am' % (arrive, name))
    # request() generates an event that lets you wait until the resource becomes available again
    # use with statement to automatically release the resource
    with counter.request() as req:  # call request from Resource()
        patience = random.uniform(min_patience, max_patience)
        results = yield req | env.timeout(patience)

        wait = env.now - arrive

        if req in results:
            # If waiting time is within customer's patience, the customer chooses to wait
            print('%7.4f %s: Waited %6.3f' % (env.now, name, wait))

            tib = random.expovariate(1 / time_in_bank)
            yield env.timeout(tib)
            print('%7.4f %s: Finished' % (env.now, name))

        else:
            # The customer chooses to leave
            print('%7.4f %s: Reneged after %4.3f' % (env.now, name, wait))


print('Bank renege')

random.seed(random_seed)
env = simpy.Environment()

# start processes and run
counter = simpy.Resource(env, capacity=1)  # capacity is how many customers are able to get services
env.process(source(env, new_customers, interval_customers, counter))  # define the process of this simulation
env.run()  # run the simulation


