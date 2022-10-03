// Copyright 2021 DeepMind Technologies Limited
//
// Licensed under the Apache License, Version 2.0 (the "License");
// you may not use this file except in compliance with the License.
// You may obtain a copy of the License at
//
//      http://www.apache.org/licenses/LICENSE-2.0
//
// Unless required by applicable law or agreed to in writing, software
// distributed under the License is distributed on an "AS IS" BASIS,
// WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
// See the License for the specific language governing permissions and
// limitations under the License.

#include "open_spiel/algorithms/dqn_torch/dqn.h"

#include <memory>
#include <random>

#include "open_spiel/abseil-cpp/absl/flags/flag.h"
#include "open_spiel/abseil-cpp/absl/flags/parse.h"
#include "open_spiel/spiel.h"
#include "open_spiel/spiel_globals.h"
#include "open_spiel/spiel_utils.h"

ABSL_FLAG(int, seed, 8263487, "Seed to use for random number generation.");

namespace open_spiel {
namespace algorithms {
namespace torch_dqn {
namespace {

void SelfPlayTute(int seed, int total_episodes, int report_every,
                  int num_eval_episodes) {
  std::cout << "Running self-play Tute" << std::endl;
  std::mt19937 rng(seed);
  std::shared_ptr<const Game> game = open_spiel::LoadGame("hearts");

  std::vector<std::unique_ptr<DQN>> dqn_agents;
  std::vector<std::unique_ptr<RandomAgent>> random_agents;
  std::vector<Agent*> agents(game->NumPlayers(), nullptr);

  for (Player p = 0; p < game->NumPlayers(); ++p) {
    int dqn_agent_seed = absl::Uniform<int>(rng, 0, 1000000);
    DQNSettings settings = {
        /*seed*/ dqn_agent_seed,
        /*use_observation*/ game->GetType().provides_observation_tensor,
        /*player_id*/ p,
        /*state_representation_size*/ game->InformationStateTensorShape()[0],
        /*num_actions*/ game->NumDistinctActions(),
        /*hidden_layers_sizes*/ {32, 32},
        /*replay_buffer_capacity*/ 100000,
        /*batch_size*/ 128,
        /*learning_rate*/ 0.01,
        /*update_target_network_every*/ 250,
        /*learn_every*/ 10,
        /*discount_factor*/ 0.99,
        /*min_buffer_size_to_learn*/ 1000,
        /*epsilon_start*/ 1.0,
        /*epsilon_end*/ 0.1,
        /*epsilon_decay_duration*/ 50000,
        /*loss_str*/ "mse",
        /*device*/ torch::kCUDA};
    dqn_agents.push_back(std::make_unique<DQN>(settings));
    int rand_agent_seed = absl::Uniform<int>(rng, 0, 1000000);
    random_agents.push_back(std::make_unique<RandomAgent>(p, rand_agent_seed));
  }

  for (int num_episodes = 0; num_episodes < total_episodes;
       num_episodes += report_every) {
    for (Player p = 0; p < game->NumPlayers(); ++p) {
      agents[p] = dqn_agents[p].get();
    }

    // Training
    RunEpisodes(&rng, *game, agents,
                /*num_episodes*/ report_every, /*is_evaluation*/ false);

    // Self-play eval.
    std::vector<double> avg_self_play_returns =
        RunEpisodes(&rng, *game, agents,
                    /*num_episodes*/ num_eval_episodes, /*is_evaluation*/ true);

    std::vector<double> avg_returns_vs_random(game->NumPlayers(), 0);
    // Eval vs. random.
    for (Player p = 0; p < game->NumPlayers(); ++p) {
      for (Player pp = 0; pp < game->NumPlayers(); ++pp) {
        if (pp == p) {
          agents[pp] = dqn_agents[pp].get();
        } else {
          agents[pp] = random_agents[pp].get();
        }
      }
      std::vector<double> avg_returns = RunEpisodes(
          &rng, *game, agents,
          /*num_episodes*/ num_eval_episodes, /*is_evaluation*/ true);
      avg_returns_vs_random[p] = avg_returns[p];
    }

    std::cout << num_episodes + report_every << " self-play returns: ";
    for (Player p = 0; p < game->NumPlayers(); ++p) {
      std::cout << avg_self_play_returns[p] << " ";
    }
    std::cout << "returns vs random: ";
    for (Player p = 0; p < game->NumPlayers(); ++p) {
      std::cout << avg_returns_vs_random[p] << " ";
    }
    std::cout << std::endl;
  }
}

}  // namespace
}  // namespace torch_dqn
}  // namespace algorithms
}  // namespace open_spiel

namespace torch_dqn = open_spiel::algorithms::torch_dqn;

int main(int argc, char** argv) {
  absl::ParseCommandLine(argc, argv);
  int seed = absl::GetFlag(FLAGS_seed);
  torch::manual_seed(seed);
  torch_dqn::SelfPlayTute(seed,
                          /*total_episodes*/ 100000,
                          /*report_every*/ 1000,
                          /*num_eval_episodes*/ 100);
  return 0;
}
