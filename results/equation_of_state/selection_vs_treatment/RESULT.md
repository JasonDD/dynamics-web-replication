# Selection against treatment: what the room term beyond shift and bend is made of

*DYNAMICS-WEB series, 3 September 2026. Script `cc_selection_tests.py`. The three part model (curved map,
room shift, ridge shrunk room bend) is fitted per person grouped fold and its held out residuals are the
material. Predictions written before the run (fabric #20219): under selection, a person level unobserved
cancels within the person, so the room pair cannot predict how the same person's residual differs between
rooms (B1 at the null) and a person's residual on the state tail predicts the tail coordinate of the rooms
they belong to (B4 above the null, homophily on the tail); under treatment B1 sits above the null and B4
does not. A first run of B1 used a null that relabelled rooms bijectively, to which the model is invariant,
and returned real = null; it was replaced by a target permutation with random sign before any result was
read.*

## B1: does the room pair predict the same person's residual difference across rooms?

| Corpus | Persons in 2+ rooms | Ordered room pairs | Held out R² | Null mean (p95) | p |
|---|---|---|---|---|---|
| Web domains | 58,826 | 1,078,470 | **+0.032** | −0.001 (−0.001) | 0.02 |
| Subreddits | 1,806 | 161,046 | −0.046 | −0.000 (−0.000) | 1.00 |

On the domains the room pair does predict how the same person's residual moves between rooms: a room
treatment beyond shift and bend, small (three per cent of the within person difference). On the
subreddits there is none.

## B4: does a person's residual on the state tail predict the tail of their other rooms?

| Corpus | Tail R² | Tail null (p95) | Plane R² | Plane null (p95) |
|---|---|---|---|---|
| Web domains | **+0.0126** | 0.000 (0.000) | +0.0048 | 0.000 (0.000) |
| Subreddits | +0.0010 | 0.000 (0.000) | +0.0007 | 0.000 (0.000) |

On the domains a person's leftover on the tail carries a little of which rooms they are in, more than
the plane does, which is the homophily on the tail that selection predicts; on the subreddits it is
nil. Residual variance shares: the person carries 52 per cent of the held out residual variance on the
domains and 95 per cent on the subreddits (53 per cent among multi room persons), the room close to zero
by construction.

## Reading

Both signatures are present on the domains and both are small: a room does a little more to the same
person than shift and bend capture (B1), and the tail of the room state carries a little of who the
room selects (B4). On the subreddits neither appears. This matches the competitor test, where a model
given room identity adds only 0.001 over one given the room's profile on either corpus: whatever the
remainder is, it is not a term tied to which room it is. The arrival and retention tests (first post
against later posts; stayers against one time posters at their first post) need dates and can run only on
the subreddit corpus, where nothing remains to explain; on the domains only 2.4 per cent of rows carry a
date.
