import pytest
from bear_utils.extras.state_tracking import StateMachine, State, StateTransitionError, auto_value_decorator


class MockStateMachine(StateMachine):
    START = State("start", initial=True)
    PROCESSING = State("processing")
    DONE = State("done", final=True)
    ERROR = State("error", final=True)


class MockStateMachineWithManualValues(StateMachine):
    IDLE = State("idle")  # value = 0
    RUNNING = State("running")  # value = 1
    WARNING = State("warning", id=10)  # Manual value = 10
    CRITICAL = State("critical")  # value = 11 (continues from manual)


class TestState:
    def test_comparison_with_states(self) -> None:
        state = State("Test")
        assert state == "Test"
        assert not state == "Another"

    def test_state_creation_positional(self) -> None:
        state = State(name="Test")
        assert state.name == "Test"
        assert not state.initial
        assert not state.final

    def test_state_creation_keyword(self):
        state = State(name="Test", initial=True, final=False)
        assert state.name == "Test"
        assert state.initial
        assert not state.final

    def test_state_with_flags(self):
        initial_state = State("Start", initial=True)
        final_state = State("End", final=True)

        assert initial_state.initial
        assert not initial_state.final
        assert final_state.final
        assert not final_state.initial

    def test_state_string_representation(self):
        state = State("Test State")
        assert str(state) == "test state"

    def test_state_equality_with_state(self):
        class MockState(StateMachine):
            STATE_A = State("A")
            STATE_B = State("B")

        mock_sm = MockState()
        state1: State = mock_sm.STATE_A
        state2: State = mock_sm.STATE_A
        state3: State = mock_sm.STATE_B

        assert state1 == state2
        assert 0 == state1  # Any enum with same value will be equal
        assert state1 != state3

    def test_state_equality_with_int(self):
        state = State("Test")
        assert state == state.id
        assert state != 999

    @pytest.mark.xfail(reason="States outside of a state machine cannot increment their values")
    def test_state_multiple_states(self):
        state = State("Test")
        state2 = State("Test2")

        assert int(state.id) == 0
        assert int(state2.id) == 1

    def test_state_int_conversion(self):
        state = State("Test")
        assert int(state) == state.id

    def test_state_hash(self):
        state = State("Test")
        assert hash(state) == hash(state.id)

    def test_manual_value_assignment(self):
        state = State("Test", id=42)
        assert state.id == 42


class TestAutoValueSystem:
    def test_string_conversion(self):
        @auto_value_decorator()
        class AutoValueStateMachine(StateMachine):
            INFO = "INFO"
            WARNING = "WARNING"
            ERROR = "ERROR"

        sm = AutoValueStateMachine()

        assert isinstance(sm.INFO, State)
        assert isinstance(sm.WARNING, State)
        assert isinstance(sm.ERROR, State)

        assert sm.INFO.id == 0
        assert sm.WARNING.id == 1
        assert sm.ERROR.id == 2

        @auto_value_decorator()
        class AutoValueStateMachine2(StateMachine):
            START = "START"
            MIDDLE = State("MIDDLE")
            END = "END"

        sm2 = AutoValueStateMachine2()
        assert isinstance(sm2.START, State)
        assert isinstance(sm2.MIDDLE, State)
        assert isinstance(sm2.END, State)
        assert sm2.START.id == 0
        assert sm2.MIDDLE.id == 1
        assert sm2.END.id == 2

    def test_auto_increment_within_class(self):
        sm = MockStateMachine()
        assert sm.START.id == 0
        assert sm.PROCESSING.id == 1
        assert sm.DONE.id == 2
        assert sm.ERROR.id == 3

    def test_auto_increment_with_manual_values(self):
        sm = MockStateMachineWithManualValues()
        assert sm.IDLE.id == 0
        assert sm.RUNNING.id == 1
        assert sm.WARNING.id == 10  # Manual id
        assert sm.CRITICAL.id == 11  # Continues from manual

    def test_separate_counters_per_class(self):
        class FirstMachine(StateMachine):
            A = State("a")
            B = State("b")

        class SecondMachine(StateMachine):
            X = State("x")
            Y = State("y")

        first = FirstMachine()
        second = SecondMachine()

        assert first.A.id == 0
        assert first.B.id == 1
        assert second.X.id == 0  # Separate counter
        assert second.Y.id == 1


class TestStateMachineInitialization:
    def test_discovers_states_from_class(self):
        sm = MockStateMachine()
        assert len(sm.state_map) == 4
        assert "start" in sm.state_map
        assert "processing" in sm.state_map
        assert "done" in sm.state_map
        assert "error" in sm.state_map

    def test_sets_initial_state_correctly(self):
        sm = MockStateMachine()
        assert sm.current_state == sm.START
        assert sm.initial_state == sm.START

    def test_fallback_when_no_initial_state(self):
        class NoInitialStateMachine(StateMachine):
            STATE_A = State("A")
            STATE_B = State("B")

        sm = NoInitialStateMachine()
        assert sm.current_state in [sm.STATE_A, sm.STATE_B]

    def test_empty_state_machine_raises_error(self):
        class EmptyStateMachine(StateMachine):
            pass

        with pytest.raises(ValueError):
            EmptyStateMachine()


class MockStateMachineHasMethod:
    def test_has_state_by_state_object(self):
        sm = MockStateMachine()
        assert sm.has(sm.START)
        assert not sm.has(State("NonExistent"))

    def test_has_state_by_name(self):
        sm = MockStateMachine()
        assert sm.has("START")
        assert not sm.has("NONEXISTENT")

    def test_has_state_by_value(self):
        sm = MockStateMachine()
        assert sm.has(sm.START.id)
        assert not sm.has(999)


class MockStateMachineGetMethods:
    def test_get_by_name_success(self):
        sm = MockStateMachine()
        state = sm._get_by_name("START")
        assert state == sm.START

    def test_get_by_name_failure(self):
        sm = MockStateMachine()
        with pytest.raises(ValueError, match="State 'None' not found"):
            sm._get_by_name("NONEXISTENT")

    def test_get_by_value_success(self):
        sm = MockStateMachine()
        state = sm._get_by_value(sm.PROCESSING.id)
        assert state == sm.PROCESSING

    def test_get_by_value_failure(self):
        sm = MockStateMachine()
        with pytest.raises(ValueError, match="State with value '999' not found"):
            sm._get_by_value(999)

    def test_get_with_state_object(self):
        sm = MockStateMachine()
        state = sm._get(sm.START)
        assert state == sm.START

    def test_get_with_string(self):
        sm = MockStateMachine()
        state = sm._get("PROCESSING")
        assert state == sm.PROCESSING

    def test_get_with_int(self):
        sm = MockStateMachine()
        state = sm._get(sm.DONE.id)
        assert state == sm.DONE

    def test_get_with_default(self):
        sm = MockStateMachine()
        result = sm._get("NONEXISTENT", default="DEFAULT")
        assert result == "DEFAULT"


class MockStateMachineStateTransitions:
    def test_valid_transition_by_state_object(self):
        sm = MockStateMachine()
        sm.current_state = sm.PROCESSING
        assert sm.current_state == sm.PROCESSING

    def test_valid_transition_by_string(self):
        sm = MockStateMachine()
        sm.current_state = "PROCESSING"
        assert sm.current_state == sm.PROCESSING

    def test_valid_transition_by_int(self):
        sm = MockStateMachine()
        sm.current_state = sm.PROCESSING.id
        assert sm.current_state == sm.PROCESSING

    def test_transition_to_same_state_is_noop(self):
        sm = MockStateMachine()
        initial = sm.current_state
        sm.current_state = sm.START  # Same as initial
        assert sm.current_state == initial

    def test_cannot_transition_from_final_state(self):
        sm = MockStateMachine()
        sm.current_state = sm.PROCESSING
        sm.current_state = sm.DONE  # Move to final state

        with pytest.raises(StateTransitionError, match="Cannot change from final state"):
            sm.current_state = sm.PROCESSING

    def test_cannot_transition_to_initial_state_from_other_state(self):
        sm = MockStateMachine()
        sm.current_state = sm.PROCESSING

        with pytest.raises(StateTransitionError, match="Cannot set initial state"):
            sm.current_state = sm.START

    def test_invalid_state_raises_value_error(self):
        sm = MockStateMachine()
        with pytest.raises(ValueError, match="State NONEXISTENT is not defined"):
            sm.current_state = "NONEXISTENT"

    def test_invalid_type_raises_type_error(self):
        sm = MockStateMachine()
        with pytest.raises(TypeError, match="Invalid state"):
            sm.current_state = []

    def test_set_state_method(self):
        sm = MockStateMachine()
        sm.set_state("PROCESSING")
        assert sm.current_state == sm.PROCESSING

    def test_multiple_final_states(self):
        sm = MockStateMachine()
        sm.current_state = sm.PROCESSING

        # Can transition to either final state
        sm.current_state = sm.ERROR
        assert sm.current_state == sm.ERROR

        # But can't transition from final state
        with pytest.raises(StateTransitionError, match="Cannot change from final state"):
            sm.current_state = sm.DONE


class TestStateMachineEdgeCases:
    def test_multiple_initial_states_picks_first_found(self):
        class MultiInitialStateMachine(StateMachine):
            STATE_A = State("A", initial=True)
            STATE_B = State("B", initial=True)

        sm = MultiInitialStateMachine()
        assert sm.current_state.initial

    def test_mixed_syntax_creation(self):
        class MixedSyntaxMachine(StateMachine):
            MIXED = State("mixed", initial=True)
            POSITIONAL = State("positional")
            KEYWORD = State(name="keyword")

        sm = MixedSyntaxMachine()
        assert sm.POSITIONAL.name == "positional"
        assert sm.KEYWORD.name == "keyword"
        assert sm.MIXED.name == "mixed"
        assert sm.current_state == sm.MIXED
