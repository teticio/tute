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
#include "open_spiel/bots/human/human_bot.h"

ABSL_FLAG(int, seed, 8263487, "Seed to use for random number generation.");
ABSL_FLAG(bool, train, false, "Train model.");

namespace open_spiel {
namespace algorithms {
namespace torch_dqn {
namespace {

class DQNTute : public DQN {
  public:
    DQNTute(Player player_id, int seed, const open_spiel::Game &game)
      : player_id_(player_id), DQN({
      /*seed*/ seed,
      /*use_observation*/ game.GetType().provides_observation_tensor,
      /*player_id*/ player_id,
      /*state_representation_size*/ game.InformationStateTensorShape()[0],
      /*num_actions*/ game.NumDistinctActions(),
      /*hidden_layers_sizes*/ {64, 64},
      /*replay_buffer_capacity*/ 100000,
      /*batch_size*/ 128,
      /*learning_rate*/ 0.01,
      /*update_target_network_every*/ 250,
      /*learn_every*/ 10,
      /*discount_factor*/ 0.99,
      /*min_buffer_size_to_learn*/ 1000,
      /*epsilon_start*/ 0.1,
      /*epsilon_end*/ 1.0,
      /*epsilon_decay_duration*/ 50000,
      /*loss_str*/ "mse"}) {}
    ~DQNTute() = default;

    void Load() {
      DQN::Load("model_" + std::to_string(player_id_),
                "optimizer_" + std::to_string(player_id_));
    }

    void Save() {
      DQN::Save("model_" + std::to_string(player_id_),
                "optimizer_" + std::to_string(player_id_));
    }

  private:
    int player_id_;
};

class DQNTuteBot : public Bot {
 public:
  DQNTuteBot(Player player_id, int seed, const open_spiel::Game &game)
    : player_id_(player_id), rng_(seed) {
    dqn_agent_ = std::make_unique<DQNTute>(player_id, seed, game);
    dqn_agent_.get()->Load();
  }
  ~DQNTuteBot() = default;

  void RestartAt(const State&) override {}
  Action Step(const State& state) override {
    if (state.IsChanceNode()) {
      // Chance node; sample one according to underlying distribution.
      open_spiel::ActionsAndProbs outcomes = state.ChanceOutcomes();
      return open_spiel::SampleAction(outcomes, rng_).first;
    } else {
      // The state must be a decision node, ask the right bot to make its
      // action.
      return dqn_agent_->Step(state);
    }
  }
  bool ProvidesPolicy() override { return false; }

 private:
  const Player player_id_;
  std::mt19937 rng_;
  std::unique_ptr<DQNTute> dqn_agent_;
};

std::pair<std::vector<double>, std::vector<std::string>>
PlayGame(int seed) {
  std::mt19937 rng(seed);  // Random number generator.

  // Create the game.
  std::shared_ptr<const open_spiel::Game> game =
      open_spiel::LoadGame("tute");
  std::vector<std::unique_ptr<open_spiel::Bot>> bots;

  for (Player p = 0; p < game->NumPlayers() - 1; ++p) {
    int bot_seed = absl::Uniform<int>(rng, 0, 1000000);
    bots.push_back(std::make_unique<torch_dqn::DQNTuteBot>(p, bot_seed, *game));
  }
  bots.push_back(std::make_unique<open_spiel::HumanBot>());

  bool quiet = false;
  std::unique_ptr<open_spiel::State> state = game->NewInitialState();
  std::vector<std::string> history;

  if (!quiet)
    std::cerr << "Initial state:\n" << state << std::endl;

  while (!state->IsTerminal()) {
    open_spiel::Player player = state->CurrentPlayer();

    open_spiel::Action action;
    if (state->IsChanceNode()) {
      // Chance node; sample one according to underlying distribution.
      open_spiel::ActionsAndProbs outcomes = state->ChanceOutcomes();
      action = open_spiel::SampleAction(outcomes, rng).first;
    } else {
      // The state must be a decision node, ask the right bot to make its
      // action.
      action = bots[player]->Step(*state);
    }
    if (!quiet)
      std::cerr << "Player " << player
                << " chose action: " << state->ActionToString(player, action)
                << std::endl;

    // Inform the other bot of the action performed.
    for (open_spiel::Player p = 0; p < bots.size(); ++p) {
      if (p != player) {
        bots[p]->InformAction(*state, player, action);
      }
    }

    // Update history and get the next state.
    history.push_back(state->ActionToString(player, action));
    state->ApplyAction(action);

    if (!quiet)
      std::cerr << "Next state:\n" << state->ToString() << std::endl;
  }

  std::cerr << "Returns: " << absl::StrJoin(state->Returns(), ", ")
            << std::endl;
  std::cerr << "Game actions: " << absl::StrJoin(history, ", ") << std::endl;

  return {state->Returns(), history};
}

void SelfPlayTute(int seed, int total_episodes, int report_every,
                  int num_eval_episodes) {
  std::cout << "Running self-play Tute" << std::endl;
  std::mt19937 rng(seed);
  std::shared_ptr<const Game> game = open_spiel::LoadGame("hearts");

  std::vector<std::unique_ptr<DQNTute>> dqn_agents;
  std::vector<std::unique_ptr<RandomAgent>> random_agents;
  std::vector<Agent*> agents(game->NumPlayers(), nullptr);

  for (Player p = 0; p < game->NumPlayers(); ++p) {
    int dqn_agent_seed = absl::Uniform<int>(rng, 0, 1000000);
    dqn_agents.push_back(std::make_unique<DQNTute>(p, dqn_agent_seed, *game));
    dqn_agents[p].get()->Load();
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

    // Save.
    for (Player p = 0; p < game->NumPlayers(); ++p) {
      dqn_agents[p].get()->Save();
    }
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
  int train = absl::GetFlag(FLAGS_train);
  torch::manual_seed(seed);
  if (train) {
    torch_dqn::SelfPlayTute(seed,
                            /*total_episodes*/ 10000000,
                            /*report_every*/ 1000,
                            /*num_eval_episodes*/ 100);
  } else {
    auto [returns, history] = torch_dqn::PlayGame(seed);
  }
  return 0;
}
