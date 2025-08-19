# SANN Changelog

## 1.0.4

* Corrected default value of rho in sigmoid function from 0.5 to (the more conventional) 1.0.
* Fixed minor bugs in the training scripts.
* Re-trained all the examples to use the sigmoid function's new default settings.

## 1.0.3

* Added "Tanks a lot" example to the documentation.

## 1.0.2

* Removed the unused `tlu` function.
* Updated tests to reflect this change.
* Minor documentation tidy-ups.

## 1.0.1

* API naming clarification:
    - Renamed `clean_ann` to `clean_network`.
    - Renamed `create_ann` to `create_network`.
* Documentation refinement.

## 1.0.0

* Initial release.
* Docs at [https://sann.readthedocs.org/](https://sann.readthedocs.org/).
* Full test coverage.
* Two examples:
    - digit recognition - character recognition via supervised backpropagation training.
    - snAIke - play the SNAKE game via unsupervised neuro-evolution training.
* Blog post exploring the concepts: [Behind the AI Curtain](https://ntoll.org/article/ai-curtain/)