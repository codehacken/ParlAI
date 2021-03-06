# Copyright (c) 2017-present, Facebook, Inc.
# All rights reserved.
# This source code is licensed under the BSD-style license found in the
# LICENSE file in the root directory of this source tree. An additional grant
# of patent rights can be found in the PATENTS file in the same directory.
from parlai.core.worlds import World, validate, create_task

class ModelEvaluatorWorld(World):
    """
    World for letting Turkers evaluate a dialog model's performance given a context.
    Assumes the context is a context from a given task, e.g. from SQuAD, CBT, etc.
    """

    evaluator_agent_id = 'Model Evaluator'

    def __init__(self, opt, model_agent, task_opt, mturk_agent):
        self.task_world = create_task(task_opt, model_agent)
        self.mturk_agent = mturk_agent
        self.episodeDone = False

        # Tell the mturk agents about the configuration
        self.mturk_agent.mturk_agent_ids = [mturk_agent.id]
        self.mturk_agent.all_agent_ids = [self.__class__.evaluator_agent_id, mturk_agent.id] # In speaking order
        
        # Create HITs for mturk agents
        self.mturk_agent.create_hit()    

    def parley(self):
        self.task_world.parley()

        ad = {}
        # Show the dialog model's response to the context, and ask the turker to rate the response
        ad['id'] = self.__class__.evaluator_agent_id
        ad['text'] = (
            self.task_world.get_acts()[0]['text'] + "\n\n" +
            "How would you rate the following response (from 0 to 10):\n\n" +
            self.task_world.get_acts()[1]['text'])

        # TODO: deal with multi-turn dialogs, for now we will just deal
        # with 1-turn dialogs in this task.
        ad['episode_done'] = True  # self.world.episode_done()
        
        self.mturk_agent.observe(validate(ad))
        rating = self.mturk_agent.act()

        self.episodeDone = True

    def episode_done(self):
        return self.episodeDone

    def report(self):
        # TODO: Add logging code here
        pass

    def shutdown(self):
        self.task_world.shutdown()
        self.mturk_agent.shutdown()
